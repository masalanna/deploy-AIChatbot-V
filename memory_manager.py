
import time
from typing import Optional

SESSION_TTL_MINUTES = 60          # Sessions expire after 60 min of inactivity
MAX_HISTORY_LENGTH  = 6           # Keep last 6 (query, answer) pairs in memory
SCHEDULE_PROMPT_EVERY = 5         # Suggest scheduling every N technical questions

KNOWN_TOPICS = [
    "boss",
    "bacnet",
    "modbus",
    "hart",
    "dmx",
    "edificeedge",
    "edificeplus",
    "edifice",
    "softbac",
    "softmod",
    "iot",
    "smart building",
    "smart factory",
    "gateway",
    "cloud",
    "aws",
    "automation",
    "energy",
    "hvac",
    "lighting",
    "security",
    "analytics",
    "industry 4.0",
    "digital twin",
    "protocol",
    "embedded",
    "firmware",
]


class ConversationSession:
    def __init__(self, session_id: str):
        self.session_id      = session_id
        self.last_topic      : Optional[str] = None   # e.g. "BOSS"
        self.last_intent     : Optional[str] = None   # "knowledge" | "casual" | "action"
        self.question_count  : int = 0                # technical questions only
        self.history         : list = []              # [{query, answer}, ...]
        self.topics_discussed: set  = set()
        self.created_at      : float = time.time()
        self.last_active     : float = time.time()


    def record(self, query: str, answer: str, intent: str = "knowledge"):
        
        self.last_active = time.time()
        self.last_intent = intent

        if intent == "knowledge":
            self.question_count += 1
            self._extract_topic(query)

        # Append and trim history
        self.history.append({"query": query, "answer": answer})
        if len(self.history) > MAX_HISTORY_LENGTH:
            self.history = self.history[-MAX_HISTORY_LENGTH:]

    # def _extract_topic(self, query: str):
        
    #     q = query.lower()
    #     for topic in KNOWN_TOPICS:          # list is ordered, specific first
    #         if topic in q:
    #             self.last_topic = topic.upper() if len(topic) <= 5 else topic.title()
    #             self.topics_discussed.add(self.last_topic)
    #             return

    def _extract_topic(self, query: str):
        q = query.lower()
        last_found = None
        for topic in KNOWN_TOPICS:
            if topic in q:
                last_found = topic        # keep scanning — take the LAST match
                self.topics_discussed.add(
                    topic.upper() if len(topic) <= 5 else topic.title()
                )
        if last_found:
            self.last_topic = last_found.upper() if len(last_found) <= 5 else last_found.title()

    def get_history_text(self, max_pairs: int = 3) -> str:
        
        if not self.history:
            return ""

        recent = self.history[-max_pairs:]
        lines = ["\n--- Recent Conversation ---"]
        for i, turn in enumerate(recent, 1):
            lines.append(f"Q{i}: {turn['query']}")
            # Only include answer preview (first 120 chars) to save tokens
            answer_preview = turn["answer"][:120].rstrip()
            if len(turn["answer"]) > 120:
                answer_preview += "..."
            lines.append(f"A{i}: {answer_preview}")
        lines.append("--- End of History ---")
        return "\n".join(lines)

    def should_suggest_scheduling(self) -> bool:
        return (
            self.question_count > 0
            and self.question_count % SCHEDULE_PROMPT_EVERY == 0
        )

    def topics_as_string(self) -> str:
        return ", ".join(self.topics_discussed) if self.topics_discussed else "None"

    def to_dict(self) -> dict:
        return {
            "session_id"       : self.session_id,
            "last_topic"       : self.last_topic,
            "last_intent"      : self.last_intent,
            "question_count"   : self.question_count,
            "topics_discussed" : list(self.topics_discussed),
            "conversation_length": len(self.history),
        }

_sessions: dict[str, ConversationSession] = {}


def get_session(session_id: str) -> ConversationSession:
    _purge_expired()                         

    if session_id not in _sessions:
        _sessions[session_id] = ConversationSession(session_id)

    return _sessions[session_id]


def clear_session(session_id: str) -> bool:
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False


def get_session_info(session_id: str) -> dict:
    if session_id not in _sessions:
        return {
            "session_id"       : session_id,
            "last_topic"       : None,
            "last_intent"      : None,
            "question_count"   : 0,
            "topics_discussed" : [],
            "conversation_length": 0,
        }
    return _sessions[session_id].to_dict()


def _purge_expired():
    ttl_seconds = SESSION_TTL_MINUTES * 60
    now = time.time()
    expired = [
        sid for sid, sess in _sessions.items()
        if (now - sess.last_active) > ttl_seconds
    ]
    for sid in expired:
        del _sessions[sid]
