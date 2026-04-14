
from utils.normalizer import normalize, needs_context_resolution, resolve_context
import memory_manager
import prompt_manager


_CASUAL_EXACT = {
    "hi", "hello", "hey", "thanks", "thank you", "okay", "ok",
    "yes", "no", "bye", "goodbye", "how are you", "who are you",
    "what are you", "how are you doing",
    # Single-word reactions — never reach knowledge pipeline
    "good", "nice", "cool", "great", "interesting", "wow", "awesome",
    "alright", "understood", "noted", "perfect", "excellent", "fine",
    "got it", "i see", "makes sense", "that helps",
    # Multi-word reactions
    "okay good", "okay great", "okay nice", "okay cool", "okay thanks",
    "oh okay", "oh nice", "oh great", "oh cool", "oh wow", "oh interesting",
    "thats good", "thats great", "thats nice", "thats cool", "thats helpful",
    "that is good", "that is great", "that is helpful",
    "sounds good", "sounds great", "sounds nice",
    "very good", "very nice", "very helpful", "very interesting",
    "thank you so much", "thanks a lot", "thanks so much",
}

_CASUAL_PREFIXES = (
    "hi ", "hello ", "hey ", "good morning", "good afternoon",
    "good evening", "good night",
)

_SCHEDULING_STRONG = {
    "schedule", "book", "arrange", "appointment",
}
_SCHEDULING_WEAK = {
    "meeting", "call", "connect", "talk", "speak", "demo",
}

_SCHEDULING_REQUEST_PHRASES = (
    "i want to", "i'd like to", "i would like to",
    "can i", "can you", "could you", "please",
    "help me", "set up", "fix a", "fix me a",
    "let's", "lets", "want to", "need to",
    "schedule a", "book a", "arrange a",
)

_DECISION_EXACT = {"yes", "no", "yeah", "nope", "yep", "yup", "nah"}



def route(raw_input: str, session_id: str) -> dict:
    if prompt_manager.is_time_query(raw_input.lower().strip()):
        response = prompt_manager.get_time_response()
        session = memory_manager.get_session(session_id)
        session.record(raw_input, response, intent="casual")
        return _result("casual", response, raw_input)

    # ---- Step 1: Normalize ----
    normalized = normalize(raw_input)

    if not normalized:
        return _result("casual", prompt_manager.CASUAL_FALLBACK, normalized)

    # ---- Step 2: Casual detection ----
    if _is_casual(normalized):
        response = prompt_manager.get_casual_response(normalized)
        # Record casual in session so last_intent is tracked
        session = memory_manager.get_session(session_id)
        session.record(normalized, response, intent="casual")
        return _result("casual", response, normalized)

    _factual_answer = prompt_manager.get_factual_override(normalized)
    if _factual_answer:
        session = memory_manager.get_session(session_id)
        session.record(normalized, _factual_answer, intent="knowledge")
        return _result("knowledge", _factual_answer, normalized)


    # ---- Step 3: Scheduling / action detection ----
    if _is_scheduling(normalized):
        session = memory_manager.get_session(session_id)
        session.record(normalized, "", intent="action")
        return _result(
            "action",
            "📅 Sure! Please fill the form to schedule a meeting.",
            normalized,
            show_form=True,
        )

    # # ---- Step 4: Pricing detection ----
    # purchase_response = prompt_manager.get_purchase_response(normalized)
    # if purchase_response:
    #     session = memory_manager.get_session(session_id)
    #     session.record(normalized, purchase_response, intent="knowledge")
    #     return _result("knowledge", purchase_response, normalized)
    # if prompt_manager.is_pricing_query(normalized):
    #     session = memory_manager.get_session(session_id)
    #     session.record(normalized, prompt_manager.PRICING_RESPONSE, intent="knowledge")
    #     return _result("pricing", prompt_manager.PRICING_RESPONSE, normalized)

    _purchase_resp = prompt_manager.get_purchase_response(normalized)
    if _purchase_resp:
        session = memory_manager.get_session(session_id)
        session.record(normalized, _purchase_resp, intent="knowledge")
        return _result("knowledge", _purchase_resp, normalized)

    # ---- Step 5: Generic pricing detection ----
    if prompt_manager.is_pricing_query(normalized):
        session = memory_manager.get_session(session_id)
        session.record(normalized, prompt_manager.PRICING_RESPONSE, intent="knowledge")
        return _result("pricing", prompt_manager.PRICING_RESPONSE, normalized)

    # ---- Step 5: Context resolution 
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

    resolved_query = _maybe_inject_topic(resolved_query, session)
    return _result("knowledge", None, resolved_query, is_followup=is_followup)



def _is_casual(normalized: str) -> bool:
    if not normalized:
        return False

    # 1. Exact match
    if normalized in _CASUAL_EXACT:
        return True

    # 2. Prefix match
    if normalized.startswith(_CASUAL_PREFIXES):
        return True

    # 3. Single-word casual
    words = normalized.split()
    if len(words) == 1 and words[0] in _CASUAL_EXACT:
        return True

    return False


def _is_scheduling(normalized: str) -> bool:
    words = set(normalized.split())

    # Tier 1: strong signals are unambiguous — fire immediately
    if words & _SCHEDULING_STRONG:
        return True

    # Tier 2: weak signal must be accompanied by a request phrase
    if not (words & _SCHEDULING_WEAK):
        return False

    return any(
        normalized.startswith(p) or (" " + p) in normalized
        for p in _SCHEDULING_REQUEST_PHRASES
    )


def _maybe_inject_topic(query: str, session) -> str:
    if not session.last_topic:
        return query

    words = query.split()
    if len(words) > 4:
        return query

    topic_lower = session.last_topic.lower()

    if topic_lower in query.lower():
        return query

    # _NON_INJECT_SINGLES = {
    #     "good", "nice", "cool", "great", "interesting", "wow", "awesome",
    #     "alright", "understood", "noted", "perfect", "excellent", "fine",
    #     "okay", "ok", "yes", "no", "thanks", "thank you", "sure", "okay good", "okay nice",
    #     "okay cool"
    # }
    # if len(words) == 1 and words[0].lower() in _NON_INJECT_SINGLES:
    #     return query

    _REACTION_WORDS = {
    "good", "nice", "cool", "great", "interesting", "wow", "awesome",
    "alright", "understood", "noted", "perfect", "excellent", "fine",
    "okay", "ok", "yes", "no", "thanks", "sure", "helpful",
    "thank you", "sure", "okay good", "okay nice",
    "okay cool"
    }
    # Single-word reaction
    if len(words) == 1 and words[0].lower() in _REACTION_WORDS:
        return query
    # Multi-word reaction: ALL words are in _REACTION_WORDS (e.g. "okay good", "oh wow")
    if len(words) <= 3 and all(w.lower() in _REACTION_WORDS for w in words):
        return query
    
    _COMPANY_ENTITY_WORDS = {
        "company", "softdel", "organisation", "organization",
        "founded", "founder", "founders", "ceo", "director", "directors",
        "headquarters", "office", "offices", "location", "address",
        "employees", "team", "staff", "management", "leadership",
        "history", "about", "vision", "mission", "clients", "customers",
        "revenue", "established", "incorporation",
    }
    _QUESTION_STARTERS = {"who", "where", "when", "why", "how", "what", "which"}

    has_question_word = bool(set(words) & _QUESTION_STARTERS)
    has_company_entity = any(w.lower() in _COMPANY_ENTITY_WORDS for w in words)

    if has_question_word and has_company_entity:
        return query  # general Softdel question — don't inject product context

    # Also block if query directly names "softdel" or "company"
    if any(w.lower() in {"softdel", "company"} for w in words):
        return query
    

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
    return {
        "intent":     intent,
        "response":   response,
        "query":      query,
        "show_form":  show_form,
        "is_followup": is_followup,
    }
