
import re

TYPO_MAP = {
    # Greetings — including 2-char repeat forms produced by collapse step
    "hii":       "hi",
    "hiii":      "hi",
    "heey":      "hey",
    "heyy":      "hey",       # "heyyy" collapses to "heyy" then maps here
    "helo":      "hello",
    "helloo":    "hello",     # "hellooooo" collapses to "helloo"
    "helllo":    "hello",
    "hellow":    "hello",
    "hai":       "hi",

    # Farewells — include 2-char repeat forms
    "byee":      "bye",       # "byeee" / "byeeee" collapse to "byee"
    "byeee":     "bye",
    "gud bye":   "goodbye",
    "good bye":  "goodbye",
    "cya":       "bye",

    # Thanks
    "thankyou":  "thank you",
    "thanku":    "thank you",
    "thnks":     "thanks",
    "thx":       "thanks",

    # Affirmatives / negatives
    "yep":       "yes",
    "yup":       "yes",
    "yeah":      "yes",
    "nope":      "no",
    "nah":       "no",

    # Common shorthands
    "ok":        "okay",
    "k":         "okay",
    "plz":       "please",
    "pls":       "please",
    "u":         "you",
    "wht":       "what",
    "wats":      "what is",
    "wat":       "what",
    "hw":        "how",
    "abt":       "about",
    "info":      "information",
    "fullform":  "full form",
    "full-form": "full form",
    "abbr":      "abbreviation",
    "expand":    "full form",
}

_CONTEXT_TRIGGER_PATTERNS = [
    r"\bit\b",
    r"\bthis\b",
    r"\bthat\b",
    r"\bthese\b",
    r"\bthose\b",
    r"\bfull form\b",
    r"\babbreviation\b",
    r"\bwhat does it mean\b",
    r"\bwhat is it\b",
    r"\btell me more\b",
    r"\bmore about it\b",
    r"\bexplain more\b",
    r"\bexplain it\b",
    r"\belaborate\b",
    r"\bwhich is better\b",
    r"\bwhich one\b",
    r"\bboth of them\b",
    r"\bthe first one\b",
    r"\bthe second one\b",
    r"\bthe latter\b",
    r"\bthe former\b",
    r"\bneither\b",
    r"\ball of them\b"
]

_COMPILED_TRIGGERS = [re.compile(p, re.IGNORECASE) for p in _CONTEXT_TRIGGER_PATTERNS]

_PREFIX_PATTERNS = [
    r"^(based on (the |this )?(context|information|documents?)[,:]?\s*)",
    r"^(according to (the |this )?(context|information|documents?)[,:]?\s*)",
    r"^(the answer is[:\s]+)",
    r"^(my (response|answer|greeting|message) is[:\s]+)",
    r"^(i would say[,:]?\s*)",
    r"^(in (this |the )?context[,:]?\s*)",
    r"^(from (the |this )?(context|documents?)[,:]?\s*)",
    r"^(sure[,!]?\s*here('s| is)[:\s]+)",
    r"^(certainly[,!]?\s*)",
    r"^(of course[,!]?\s*)",
    r"^(great (question)?[,!]?\s*)",
    r"^(absolutely[,!]?\s*)",
]

_COMPILED_PREFIXES = [re.compile(p, re.IGNORECASE) for p in _PREFIX_PATTERNS]


_RE_COLLAPSE_TO_TWO = re.compile(r"(.)\1{2,}")   # 3+ identical chars -> 2
_RE_COLLAPSE_TO_ONE = re.compile(r"(.)\1+")       # any repeated char  -> 1
_RE_STRIP_WORD_PUNCT = re.compile(r"^[^a-z0-9]+|[^a-z0-9]+$")


def _collapse_word(word):
    c2 = _RE_COLLAPSE_TO_TWO.sub(lambda m: m.group(1) * 2, word)
    if c2 in TYPO_MAP:
        return TYPO_MAP[c2]

    c1 = _RE_COLLAPSE_TO_ONE.sub(r"\1", word)
    if c1 in TYPO_MAP:
        return TYPO_MAP[c1]

    return c2


def normalize(raw_input):
    if not raw_input or not isinstance(raw_input, str):
        return ""

    text = raw_input.strip()
    text = re.sub(r"\s+", " ", text)
    lowered = text.lower()
    lowered = re.sub(r"softdel's\b", "softdel", lowered)
    lowered = re.sub(r"'s\b", "s", lowered)
    lowered = re.sub(r"n't\b", "nt", lowered)
    lowered = re.sub(r"'re\b", "re", lowered)
    lowered = re.sub(r"'ve\b", "ve", lowered) 
    lowered = re.sub(r"'ll\b", "ll", lowered)
    lowered = re.sub(r"'m\b",  "m",  lowered)

    # Step 4: per-word punctuation strip
    raw_words = lowered.split()
    clean_words = []
    for w in raw_words:
        stripped = _RE_STRIP_WORD_PUNCT.sub("", w)
        if stripped:
            clean_words.append(stripped)

    if not clean_words:
        return ""

    # Step 5: collapse repeats + first-pass typo map
    collapsed = [_collapse_word(w) for w in clean_words]

    # Step 6: word-level typo map
    corrected = [TYPO_MAP.get(w, w) for w in collapsed]
    result = " ".join(corrected)

    # Step 7: multi-word typo map
    for typo, canonical in TYPO_MAP.items():
        if " " in typo and typo in result:
            result = result.replace(typo, canonical)

    return result.strip()


def needs_context_resolution(normalized_input):
    for pattern in _COMPILED_TRIGGERS:
        if pattern.search(normalized_input):
            return True
    return False


def resolve_context(normalized_input, last_topic):
    if not last_topic:
        return normalized_input

    q = normalized_input.strip().lower()

    if q in ("it", "this", "that", "these", "those"):
        return last_topic

    if re.search(r"\bfull form\b|\babbreviation\b", q):
        return "full form of " + last_topic

    if re.search(r"\bwhat is it\b|\bwhat does it mean\b", q):
        return "what is " + last_topic

    if re.search(r"\bexplain\b|\belaborate\b", q):
        return "explain " + last_topic

    if re.search(r"\btell me more\b|\bmore about it\b", q):
        return "tell me more about " + last_topic
    
    if re.search(r"\bwhich is better\b|\bwhich one\b", q):
        return f"compare {last_topic} features and benefits"

    if re.search(r"\bboth of them\b|\ball of them\b", q):
        return f"all features of {last_topic}"

    # Generic fallback: replace pronoun inline
    cleaned = re.sub(r"\b(it|its|this|that|these|those)\b",
                     last_topic, q, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(r"\babout\s*$", "", cleaned).strip()
    return cleaned


def clean_llm_output(text):
    if not text:
        return ""

    cleaned = text.strip()
    for pattern in _COMPILED_PREFIXES:
        # cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = pattern.sub("", cleaned).strip()
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]

    return cleaned
