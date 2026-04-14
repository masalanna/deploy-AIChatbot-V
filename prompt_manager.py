import re
RAG_TEMPLATE = """\
You are SVA — Softdel Virtual Assistant 🤖.
Your job is to answer questions about Softdel's products, services,
IoT solutions, smart buildings, smart factories, and digital transformation.

════════════════════════════════════════
STRICT RULES — follow every single one:
════════════════════════════════════════
1. Answer ONLY from the Context section below.
   If the context does not contain enough information, say exactly:
   "❌ I could not find the answer for that topic. 📞 Would you like me to schedule a call with one of our executives to discuss this further?"

2. NEVER reveal pricing, costs, rates, fees, or any financial figures.
   If pricing appears in context, ignore it and say:
   "For pricing information, please contact our sales team directly."

3. NEVER use any of these filler phrases:
   • "Based on the context"       • "According to the context"
   • "The answer is"              • "I would say"
   • "My response is"             • "Based on the information provided"
   • "Certainly!"                 • "Great question!"
   • "Of course!"                 • "Absolutely!"

4. Respond directly and naturally — as if talking to a knowledgeable colleague.

5. Keep answers concise: 2–4 sentences for facts, up to 6 for complex topics.

6. Use emojis and light formatting to keep the answer engaging and readable.

7. After EVERY knowledge answer append this EXACT block format.
   Replace the placeholder text with real Softdel-relevant topics.
   Pick 3 topics the user has NOT yet discussed (vary them each time).
   CRITICAL: Write topic names as plain text — NO brackets, NO quotes,
   NO parentheses, NO markdown formatting around the topic name itself.
You might also be interested in:
• 🌐 Topic name here
• 🏭 Topic name here
• ⚡ Topic name here

════════════════════════════════════════
HARD-CODED ANSWERS (reproduce these verbatim when the question matches):
════════════════════════════════════════
Q: What are Softdel's products?
A: Our product portfolio includes:
• Communication protocol stacks (e.g. BACnet, Modbus, HART, DMX)
• IoT Gateway & Platform solutions (e.g. EdificeEdge, EdificePlus)
• A BACnet simulator (BOSS) for testing and simulation of devices over IP networks

Q: What skills are typically required at Softdel?
A: Some commonly used skills are:
• Embedded firmware / hardware protocol experience (SPI, I2C, UART)
• Cloud / AWS services, microservices, REST APIs, NoSQL/SQL databases
• DevOps, CI/CD pipelines, testing automation, edge computing

════════════════════════════════════════
SESSION CONTEXT:
Topics already discussed (do NOT suggest these again): {topics_discussed}
{history}
════════════════════════════════════════
CONTEXT (retrieved from Softdel knowledge base):
{context}
════════════════════════════════════════

Current Question: {query}

Answer:"""


FOLLOWUP_TEMPLATE = """You are SVA — Softdel Virtual Assistant 🤖.

════════════════════════════════════════
FOLLOW-UP INSTRUCTIONS — READ CAREFULLY:
════════════════════════════════════════
The user is asking a FOLLOW-UP question about something already discussed.
Their previous question and your previous answer are in the CONVERSATION
HISTORY section below.

Your job:
1. DO NOT repeat or rephrase what you already said in the previous answer.
2. EXPAND on the topic — provide additional depth, details, sub-features,
   use cases, technical specifics, or examples that were NOT in the previous answer.
3. If the context below contains new information beyond the previous answer,
   use it. If not, explicitly say:
   "I've shared everything available on this topic. Would you like to
   schedule a call with our team to discuss further? 📞"
4. Keep the answer fresh and additive — the user already knows the basics.

════════════════════════════════════════
STRICT RULES (same as always):
════════════════════════════════════════
• Answer ONLY from the Context section below.
• NEVER reveal pricing, costs, rates, or financial figures.
• NEVER use filler phrases: "Based on the context", "The answer is",
  "I would say", "Certainly!", "Great question!", "Of course!".
• Respond directly and naturally.
• Use emojis and light formatting.

After your answer, append:
You might also be interested in:
• 🌐 Topic name here
• 🏭 Topic name here
• ⚡ Topic name here
(Plain text only — no brackets, quotes, or markdown around topic names.)

════════════════════════════════════════
CONVERSATION HISTORY (what was already covered — DO NOT repeat this):
{history}
════════════════════════════════════════
CONTEXT (retrieved from Softdel knowledge base — use NEW details from here):
{context}
════════════════════════════════════════

Follow-up Question: {query}

Answer (expand beyond the previous response, provide new details):"""



FOCUSED_FACT_TEMPLATE = """\
You are SVA — Softdel Virtual Assistant 🤖.

The user is asking for a single specific fact. Your job is to find that
exact fact in the Context below and return ONLY that fact.

════════════════════════════════════════
STRICT RULES FOR THIS RESPONSE:
════════════════════════════════════════
1. Answer in ONE sentence maximum. No paragraphs.
2. Give ONLY the specific fact that was asked. Nothing else.
3. Do NOT add explanation, background, or related information.
4. Do NOT add "You might also be interested in" section.
5. Do NOT add topic suggestions of any kind.
6. If the fact is not in the context, say exactly:
   "I could not find that specific information. 📞 Would you like to
   schedule a call with our team?"
7. NEVER reveal pricing or financial figures.
8. Use one emoji maximum.

Examples of the correct format:
  Q: full form of BOSS
  A: 🔤 BOSS stands for **BACnet Over IP Simulation System**.

  Q: how many devices can BOSS support
  A: ✅ BOSS supports up to **255 devices** (1 router + 254 virtual),
    including one virtual router and all associated virtual devices. 
    In addition, it can discover up to 1,000 BACnet devices available on the same network.

  Q: does BOSS support Windows 11
  A: ✅ Yes, BOSS supports Windows 10 and above, including Windows 11.

  Q: what is the minimum RAM for BOSS
  A: 💻 The minimum RAM requirement for BOSS is **4 GB**.

════════════════════════════════════════
CONTEXT:
{context}
════════════════════════════════════════

Question: {query}

Answer (one sentence only):"""


# Single-fact query detection patterns
_SINGLE_FACT_PATTERNS = [
    # Full form / abbreviation
    r"\bfull form\b",
    r"\babbreviation\b",
    r"\bstand for\b",
    r"\bstands for\b",
    r"\bshort for\b",
    r"\bwhat does \w+ mean\b",
    r"\bexpand \w+\b",

    # Yes/No capability questions
    r"\bdoes .+ support\b",
    r"\bcan .+ run\b",
    r"\bcan .+ support\b",
    r"\bis .+ (free|paid|open.source|available|compatible)\b",
    r"\bdoes .+ work (on|with)\b",

    # Single numerical facts
    r"\bhow many\b",
    r"\bmaximum (number|count|limit|devices|objects)\b",
    r"\bminimum (requirement|ram|processor|spec)\b",
    r"\bwhat (version|is the version)\b",

    # Single name/date/location facts  
    r"\bwho (is|was|are) (the )?(ceo|founder|director|md|chairman)\b",
    r"\bwhen was .+ founded\b",
    r"\bwhere is .+ (headquarter|located|office|based)\b",
]

_COMPILED_FACT_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in _SINGLE_FACT_PATTERNS
]


def is_single_fact_query(normalized_input: str) -> bool:
    """
    Returns True if the query is asking for a single specific fact
    that should be answered in one sentence with no elaboration.

    Used by rag_engine to select FOCUSED_FACT_TEMPLATE instead of
    RAG_TEMPLATE, preventing the LLM from adding unrelated context.
    """
    for pattern in _COMPILED_FACT_PATTERNS:
        if pattern.search(normalized_input):
            return True
    return False



NO_CONTEXT_RESPONSE = (
    "❌ I could not find the answer for that topic in our knowledge base.\n\n"
    "📞 Would you like me to schedule a call with one of our executives "
    "to discuss this further?"
)



PRICING_RESPONSE = """\
💰 **Pricing & Quotations**

Thank you for your interest in Softdel's solutions!

For accurate pricing, custom quotes, and cost estimates tailored to your \
specific requirements, please reach out to our sales team:

📞 **Contact Options:**
• Schedule a call with our executive
• Email us at info@softdel.com for a detailed quotation
• Discuss your project requirements directly with our team

ℹ️ *Pricing varies based on project scope, features, customisation needs, \
and deployment requirements. Our team will provide a personalised quote.*

Would you like me to schedule a call with one of our executives?"""


SCHEDULING_NUDGE = (
    "\n\n📞 *Since you've shown great interest in our solutions, "
    "would you like to schedule a call with one of our executives "
    "to discuss this further?*"
)


CASUAL_RESPONSES: dict = {
    # Identity questions
    "who are you": (
        "😊 I'm SVA — Softdel's Virtual Assistant 🤖. "
        "I'm here to help you explore Softdel's IoT solutions, smart buildings, "
        "smart factories, and digital transformation services!"
    ),
    "what are you": (
        "🤖 I'm SVA, Softdel's AI-powered virtual assistant. "
        "Ask me anything about our products, services, or solutions!"
    ),

    # Wellbeing
    "how are you doing": "👍 All good here! Ready to help. What's on your mind?",
    "how are you":       "👍 I'm doing great, thank you! How can I help you today?",

    # Greetings (shorter keys after longer to avoid early substring match)
    "hello": "👋 Hello! I'm SVA, Softdel's Virtual Assistant 🤖. How can I assist you?",
    "hey":   "👋 Hey! What would you like to know about Softdel?",
    "hi":    "👋 Hi there! How can I help you today?",

    # Thanks
    "thank you": "😊 Happy to help! Feel free to ask anything else.",
    "thanks":    "😊 You're welcome! Let me know if there's anything else I can help with.",

    # Affirmations
    "okay": "👍 Got it! Feel free to ask me anything.",
    "yes":  "👍 Sure! What would you like to know?",
    "no":   "No problem! Let me know if you need anything.",

    # Farewells
    "goodbye": "👋 Bye! If you need anything later, feel free to return. Have a wonderful day! 🌟",
    "bye":     "👋 Goodbye! Have a great day. Come back anytime!",
}

# Fallback for casual inputs that don't hit any key above
CASUAL_FALLBACK = "😊 I'm here to help! Feel free to ask me anything about Softdel."


FACTUAL_OVERRIDES = [
    {
        "triggers": [
            "full form of boss", "what does boss stand for",
            "boss stand for", "boss abbreviation", "boss full form",
            "expand boss", "what is boss short for", "what is the full form of BOSS","full form of BOSS"
        ],
        "answer": (
            "🔤 **BOSS** stands for **BACnet Over IP Simulation System**.\n\n"
            "It is Softdel's BACnet simulator for testing and simulating "
            "BACnet devices, properties, and services over IP networks."
        ),
    },
    {
        "triggers": [
            "when was softdel founded", "when was the company founded",
            "when was softdel established", "softdel founding year",
            "year softdel was founded", "softdel established",
        ],
        "answer": (
            "🏢 Softdel Systems Private Limited was **founded in 1999**.\n\n"
            "It has grown into a leading IoT and embedded technology company "
            "headquartered in Pune, India."
        ),
    },
    {
        "triggers": [
            "who founded softdel", "who started softdel",
            "softdel founder", "who is the founder",
            "who founded the company", "who started the company",
        ],
        "answer": (
            "👤 Softdel was founded by **Sunil K. Dalal**, "
            "who serves as the Founder and Chairman.\n\n"
            "The company is led by **Sachin Deshmukh** as Managing Director."
        ),
    },
    {
        "triggers": [
            "where is softdel", "softdel headquarters", "softdel hq",
            "softdel address", "where is your headquarters",
            "where is the company", "softdel location", "softdel office",
            "where is your company headquarters", "company headquarters",
        ],
        "answer": (
            "📍 Softdel's headquarters is located at:\n\n"
            "**3rd Floor, Pentagon P4, Magarpatta City,\n"
            "Hadapsar, Pune – 411028, Maharashtra, India.**\n\n"
            "Softdel also has offices in the **USA, Singapore, and Japan**."
        ),
    },
    {
        "triggers": [
            "who is the ceo", "who is ceo of softdel",
            "softdel ceo", "who leads softdel",
            "who is the managing director", "softdel management",
            "ceo of the company", "who is ceo of the company",
        ],
        "answer": (
            "👔 **Sachin Deshmukh** is the Managing Director of Softdel Systems.\n\n"
            "**Sunil K. Dalal** is the Founder and Chairman."
        ),
    },
]


def get_factual_override(normalized_input: str):
    q = normalized_input.lower().strip()
    for item in FACTUAL_OVERRIDES:
        if any(trigger in q for trigger in item["triggers"]):
            return item["answer"]
    return None

TIME_PATTERNS = [
    "what time is it",
    "what is the time",
    "what is the current time",
    "current time",
    "tell me the time",
    "whats the time",
    "time now",
    "what time",
    "the time",
]


def get_time_response() -> str:
    try:
        from datetime import datetime
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%A, %B %d %Y")
        msg = "🕐 The current time is **" + time_str + " IST**\n"
        msg += date_str + "\n\n"
        msg += "Is there anything else I can help you with?"
        return msg
    except Exception:
        from datetime import datetime
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        msg = "🕐 The current time is **" + time_str + "** (local time)\n\n"
        msg += "Is there anything else I can help you with?"
        return msg


def is_time_query(normalized_input: str) -> bool:
    """Returns True if the input is asking for the current time."""
    q = normalized_input.lower().strip()
    return any(pattern in q for pattern in TIME_PATTERNS)

PRODUCT_PURCHASE_RESPONSES = {
    "boss": (
        "✅ Yes, you can purchase the BOSS tool directly!\n\n"
        "🛒 **Buy BOSS here:**\n"
        "https://products.softdel.com/checkout/?add-to-cart=48128&quantity=1\n\n"
        "If you need help with licensing or bulk orders, contact us at "
        "info@softdel.com 📧"
    ),
}

_PURCHASE_INTENT_WORDS = {
    "purchase", "buy", "buying", "acquire",
    "get", "obtain", "directly purchase", "how to get",
    "where to buy", "can i buy", "can i purchase",
    "how can i buy", "how do i buy", "how to buy",
    "how to purchase",
}


def get_purchase_response(normalized_input: str):
    q = normalized_input.lower()
    has_intent = any(w in q for w in _PURCHASE_INTENT_WORDS)
    if not has_intent:
        return None
    for product_key, response in PRODUCT_PURCHASE_RESPONSES.items():
        if product_key in q:
            return response
    return None

PRICING_PATTERNS = [
    # Explicit price/cost questions
    "how much", "what is the price", "what does it cost", "cost of",
    "price of", "pricing for", "quote for", "quotation for", "estimate for",
    "pricing structure", "pricing model", "subscription price", "license cost",
    "total cost", "project cost", "development cost", "what will it cost",
    "give me a quote", "send me a quote", "get a quote", "request a quote",
    "pricing details", "pricing information", "how much does", "how much would",
    "purchase", "buy", "buying", "procure", "procurement",
    "can i buy", "can i purchase", "how to buy", "how to purchase",
    "where to buy", "where can i buy", "license fee", "license price", "how much is the license"
]


# def build_rag_prompt(
#     context: str,
#     query: str,
#     history: str = "",
#     topics_discussed: str = "None",
#     is_followup: bool = False,
# ) -> str:
#     if is_followup and history:
#         return FOLLOWUP_TEMPLATE.format(
#             context=context,
#             query=query,
#             history=history,
#         )
#     return RAG_TEMPLATE.format(
#         context=context,
#         query=query,
#         history=history,
#         topics_discussed=topics_discussed,
#     )

def build_rag_prompt(
    context: str,
    query: str,
    history: str = "",
    topics_discussed: str = "None",
    is_followup: bool = False,
    is_single_fact: bool = False,
) -> str:
    if is_single_fact:
        # Single-fact queries get a focused prompt — no elaboration
        return FOCUSED_FACT_TEMPLATE.format(
            context=context,
            query=query,
        )
    if is_followup and history:
        return FOLLOWUP_TEMPLATE.format(
            context=context,
            query=query,
            history=history,
        )
    return RAG_TEMPLATE.format(
        context=context,
        query=query,
        history=history,
        topics_discussed=topics_discussed,
    )


def get_casual_response(normalized_input: str) -> str:
    # 1. Exact match
    if normalized_input in CASUAL_RESPONSES:
        return CASUAL_RESPONSES[normalized_input]

    # 2. Substring match (keys ordered specific → generic in the dict)
    for key, response in CASUAL_RESPONSES.items():
        if key in normalized_input:
            return response

    # 3. Fallback
    return CASUAL_FALLBACK


def is_pricing_query(normalized_input: str) -> bool:
    q = normalized_input.lower()
    return any(pattern in q for pattern in PRICING_PATTERNS)
