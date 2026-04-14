from utils.normalizer import normalize, needs_context_resolution, resolve_context
import memory_manager
import prompt_manager

_CASUAL_EXACT = {
    "hi", "hello", "hey", "thanks", "thank you", "okay", "ok",
    "yes", "no", "bye", "goodbye", "how are you", "who are you",
    "what are you", "how are you doing",
    # Single-word reactions — must never reach knowledge pipeline
    "good", "nice", "cool", "great", "interesting", "wow", "awesome",
    "alright", "understood", "noted", "perfect", "excellent", "fine",
    "got it", "i see", "makes sense", "that helps",
    # Multi-word reactions
    "okay good", "okay great", "okay nice", "okay cool", "okay thanks", "okay thank you", "okay thankyou",
    "oh okay", "oh nice", "oh great", "oh cool", "oh wow",
    "thats good", "thats great", "thats nice", "thats cool", "thats helpful",
    "that is good", "that is great", "that is helpful",
    "sounds good", "sounds great", "sounds nice",
    "very good", "very nice", "very helpful", "very interesting",
    "thank you so much", "thanks a lot", "thanks so much", "okay bye",
    "okay then bye","okay then thank you","okay then thankyou"
}

_CASUAL_PREFIXES = (
    "hi ", "hello ", "hey ", "good morning", "good afternoon",
    "good evening", "good night",
)

# Scheduling 
_SCHEDULING_STRONG = {"schedule", "book", "arrange", "appointment"}
_SCHEDULING_WEAK   = {"meeting", "call", "connect", "talk", "speak", "demo"}
_SCHEDULING_REQUEST_PHRASES = (
    "i want to", "i'd like to", "i would like to",
    "can i", "can you", "could you", "please",
    "help me", "set up", "fix a", "fix me a",
    "let's", "lets", "want to", "need to",
    "schedule a", "book a", "arrange a",
)


def route(raw_input: str, session_id: str) -> dict:
    # ---- Step 0: Time query ----
    if prompt_manager.is_time_query(raw_input.lower().strip()):
        response = prompt_manager.get_time_response()
        session = memory_manager.get_session(session_id)
        session.record(raw_input, response, intent="casual")
        return _result("casual", response, raw_input)

    # ---- Step 1: Normalize ----
    normalized = normalize(raw_input)
    if not normalized:
        return _result("casual", prompt_manager.CASUAL_FALLBACK, "")

    # ---- Step 2: Casual detection ----
    if _is_casual(normalized):
        response = prompt_manager.get_casual_response(normalized)
        session = memory_manager.get_session(session_id)
        session.record(normalized, response, intent="casual")
        return _result("casual", response, normalized)
    normalized = _strip_greeting_prefix(normalized)
    # ---- Step 3: Scheduling detection ----
    if _is_scheduling(normalized):
        session = memory_manager.get_session(session_id)
        session.record(normalized, "", intent="action")
        return _result(
            "action",
            "📅 Sure! Please fill the form to schedule a meeting.",
            normalized,
            show_form=True,
        )

    # ---- Step 4: Context resolution ----
    # MUST happen before pricing/purchase check.
    # "how can i buy it"  → resolves "it"=BOSS → "how can i buy BOSS"
    # "can i purchase it" → resolves "it"=BOSS → "can i purchase BOSS"
    # Without this, "buy it" hits pricing guard before "it" is resolved,
    # and "BOSS" is never seen by the purchase check.
    resolved_query = normalized
    session = memory_manager.get_session(session_id)
    is_followup = False

    if needs_context_resolution(normalized):
        if session.last_topic:
            resolved_query = resolve_context(normalized, session.last_topic)
            is_followup = True
            print(f"[intent_router] Resolved: '{normalized}' → '{resolved_query}'")
        else:
            clarification = (
                "🤔 Could you be a bit more specific? "
                "Which Softdel product or topic are you referring to?"
            )
            session.record(normalized, clarification, intent="casual")
            return _result("casual", clarification, normalized)

    # ---- Step 5: Pricing / purchase check ----
    # Runs on the RESOLVED query — so "buy it" is now "buy BOSS" if applicable.
    # Your suggestion (nested if) — cleaner than two separate checks.
    if prompt_manager.is_pricing_query(resolved_query):
        # Check whether this is about a specific purchasable product first.
        purchase_resp = prompt_manager.get_purchase_response(resolved_query)
        if purchase_resp:
            # Product-specific purchase — return direct link
            session.record(resolved_query, purchase_resp, intent="knowledge")
            return _result("knowledge", purchase_resp, resolved_query,
                           is_followup=is_followup)
        else:
            # Generic pricing query — return standard deflection
            session.record(resolved_query, prompt_manager.PRICING_RESPONSE,
                           intent="knowledge")
            return _result("pricing", prompt_manager.PRICING_RESPONSE,
                           resolved_query, is_followup=is_followup)

    # ---- Step 6: Factual overrides ----
    # Known facts that must always answer correctly regardless of retrieval.
    # Full form of BOSS, founding date, HQ address, CEO etc.
    factual_resp = prompt_manager.get_factual_override(resolved_query)
    if factual_resp:
        session.record(resolved_query, factual_resp, intent="knowledge")
        return _result("knowledge", factual_resp, resolved_query,
                       is_followup=is_followup)

    # ---- Step 7: Short follow-up injection ----
    resolved_query = _maybe_inject_topic(resolved_query, session)

    # ---- Step 8: Knowledge (default) ----
    return _result("knowledge", None, resolved_query, is_followup=is_followup)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _is_casual(normalized: str) -> bool:
    """
    Returns True ONLY for pure casual inputs — no real question attached.
    
    "hi there"                → True   (pure greeting)
    "hi how are you"          → True   (greeting + casual phrase)
    "hi can you explain BOSS" → False  (greeting + real question — route to knowledge)
    """
    if not normalized:
        return False

    # Exact match — always casual
    if normalized in _CASUAL_EXACT:
        return True

    # Single-word casual
    words = normalized.split()
    if len(words) == 1 and words[0] in _CASUAL_EXACT:
        return True

    # Prefix match — only pure casual if remainder is also casual
    for prefix in _CASUAL_PREFIXES:
        if normalized.startswith(prefix):
            remainder = normalized[len(prefix):].strip()
            # No remainder — pure greeting
            if not remainder:
                return True
            # Remainder is a known casual phrase ("how are you", "thanks" etc.)
            if remainder in _CASUAL_EXACT:
                return True
            # Single filler word after greeting
            if len(remainder.split()) == 1 and remainder in {
                "there", "everyone", "all", "guys", "team", "sir", "mam", "buddy",
            }:
                return True
            # Has real content — NOT pure casual
            return False

    return False


def _strip_greeting_prefix(normalized: str) -> str:
    """
    If the input starts with a casual greeting prefix followed by a real
    question, strip the greeting and return just the question.

    "hi can you explain about boss"  → "can you explain about boss"
    "hello what is bacnet"           → "what is bacnet"
    "hey how does boss work"         → "how does boss work"
    "hi there"                       → "hi there"  (pure casual, unchanged)
    "hi how are you"                 → "hi how are you"  (pure casual, unchanged)
    """
    for prefix in _CASUAL_PREFIXES:
        if normalized.startswith(prefix):
            remainder = normalized[len(prefix):].strip()

            # No real content — pure casual, return unchanged
            if not remainder:
                return normalized

            # Remainder is casual — pure casual, return unchanged
            if remainder in _CASUAL_EXACT:
                return normalized

            # Single filler word — return unchanged
            if len(remainder.split()) == 1 and remainder in {
                "there", "everyone", "all", "guys", "team", "sir", "mam", "buddy",
            }:
                return normalized

            # Real question after greeting — return just the question
            return remainder

    return normalized

def _is_scheduling(normalized: str) -> bool:
    """
    True only when user is requesting a scheduling action.
    Tier 1: strong signals (schedule/book/arrange/appointment) fire alone.
    Tier 2: weak signals (call/meeting/demo etc.) need a request phrase.
    """
    words = set(normalized.split())

    if words & _SCHEDULING_STRONG:
        return True
    if words & _SCHEDULING_WEAK:
        if "about" in normalized or "regarding" in normalized or "on" in normalized:
            return False
    
    if not (words & _SCHEDULING_WEAK):
        return False

    return any(
        normalized.startswith(p) or (" " + p) in normalized
        for p in _SCHEDULING_REQUEST_PHRASES
    )


# def _maybe_inject_topic(query: str, session) -> str:
#     """
#     For short follow-up queries with no explicit topic, append last_topic.
#     Only fires when ALL conditions are true:
#       - last_topic is set
#       - query is 4 words or fewer
#       - last_topic not already in query
#       - query contains no OTHER known topic
#       - query is not a reaction word / general company question
#     """
#     if not session.last_topic:
#         return query

#     words = query.split()
#     if len(words) > 4:
#         return query

#     topic_lower = session.last_topic.lower()

#     if topic_lower in query.lower():
#         return query

#     # Reaction / affirmation words — not a follow-up
#     _REACTION_WORDS = {
#         "good", "nice", "cool", "great", "interesting", "wow", "awesome",
#         "alright", "understood", "noted", "perfect", "excellent", "fine",
#         "okay", "ok", "yes", "no", "thanks", "sure", "helpful",
#     }
#     if len(words) == 1 and words[0].lower() in _REACTION_WORDS:
#         return query
#     # Multi-word reaction: all words are reaction words
#     if len(words) <= 3 and all(w.lower() in _REACTION_WORDS for w in words):
#         return query

#     # General company question — question word + company/org entity word
#     _COMPANY_ENTITY_WORDS = {
#         "company", "softdel", "organisation", "organization",
#         "founded", "founder", "founders", "ceo", "director",
#         "headquarters", "office", "offices", "location", "address",
#         "employees", "team", "staff", "management", "leadership",
#         "history", "vision", "mission", "clients", "revenue", "established",
#     }
#     _QUESTION_STARTERS = {"who", "where", "when", "why", "how", "what", "which"}

#     has_question = bool(set(words) & _QUESTION_STARTERS)
#     has_company  = any(w.lower() in _COMPANY_ENTITY_WORDS for w in words)
#     if has_question and has_company:
#         return query

#     if any(w.lower() in {"softdel", "company"} for w in words):
#         return query

#     # Different known topic in query — don't override
#     from memory_manager import KNOWN_TOPICS
#     for known in KNOWN_TOPICS:
#         if known != topic_lower and known in query.lower():
#             return query

#     injected = f"{query} of {session.last_topic}"
#     print(f"[intent_router] Short follow-up injected: '{query}' → '{injected}'")
#     return injected


def _maybe_inject_topic(query: str, session) -> str:
    """
    For short follow-up queries with no explicit topic, append last_topic.
    Only fires when ALL conditions are true:
      - last_topic is set
      - query is 4 words or fewer
      - last_topic not already in query
      - query contains no OTHER known topic
      - query is not a reaction word / general company question
    """
    if not session.last_topic:
        return query

    words = query.split()
    if len(words) > 6:
        return query

    topic_lower = session.last_topic.lower()

    if topic_lower in query.lower():
        return query

    # Reaction / affirmation words — not a follow-up
    _REACTION_WORDS = {
        "good", "nice", "cool", "great", "interesting", "wow", "awesome",
        "alright", "understood", "noted", "perfect", "excellent", "fine",
        "okay", "ok", "yes", "no", "thanks", "sure", "helpful",
    }
    if len(words) == 1 and words[0].lower() in _REACTION_WORDS:
        return query
    # Multi-word reaction: all words are reaction words
    if len(words) <= 3 and all(w.lower() in _REACTION_WORDS for w in words):
        return query

    # General company question — question word + company/org entity word
    _COMPANY_ENTITY_WORDS = {
        "company", "softdel", "organisation", "organization",
        "founded", "founder", "founders", "ceo", "director",
        "headquarters", "office", "offices", "location", "address",
        "employees", "team", "staff", "management", "leadership",
        "history", "vision", "mission", "clients", "revenue", "established",
    }
    _QUESTION_STARTERS = {"who", "where", "when", "why", "how", "what", "which"}

    has_question = bool(set(words) & _QUESTION_STARTERS)
    has_company  = any(w.lower() in _COMPANY_ENTITY_WORDS for w in words)
    if has_question and has_company:
        return query

    if any(w.lower() in {"softdel", "company"} for w in words):
        return query

    # FIX 1: "softdel" as substring catches possessive/compound forms
    # "softdel's global presence" → "softdel's" contains "softdel" → block
    # The word-level check above catches "softdel" exact; this catches "softdel's"
    if any("softdel" in w.lower() for w in words):
        return query

    # FIX 2: Possessive company entities
    # "company's headquarters" → strip "'s" → "company" → in _COMPANY_ENTITY_WORDS
    # "team's strategy"        → strip "'s" → "team"    → in _COMPANY_ENTITY_WORDS
    import re as _re
    stripped_words = [_re.sub(r"'s$|s'$", "", w.lower()) for w in words]
    if any(w in _COMPANY_ENTITY_WORDS for w in stripped_words):
        return query

    # Different known topic in query — don't override
    from memory_manager import KNOWN_TOPICS
    for known in KNOWN_TOPICS:
        if known != topic_lower and known in query.lower():
            return query

    injected = f"{query} of {session.last_topic}"
    print(f"[intent_router] Short follow-up injected: '{query}' → '{injected}'")
    return injected


def _result(
    intent: str,
    response,
    query: str,
    show_form: bool = False,
    is_followup: bool = False,
) -> dict:
    """Build the standard routing result dict."""
    return {
        "intent":      intent,
        "response":    response,
        "query":       query,
        "show_form":   show_form,
        "is_followup": is_followup,
    }
