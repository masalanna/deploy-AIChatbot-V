
import os
import re
import warnings
from openai import OpenAI
from dotenv import load_dotenv

import vector_store
import memory_manager
import prompt_manager
from utils.normalizer import (
    needs_context_resolution,
    resolve_context,
    clean_llm_output,
)

warnings.filterwarnings("ignore")
load_dotenv()


GROQ_MODEL   = "llama-3.3-70b-versatile"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS  = 1024

_client: OpenAI | None = None



def initialize():
    global _client

    print("[rag_engine] Initializing...")

    # 1. Vector store (FAISS + embeddings)
    vector_store.initialize()

    # 2. LLM client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "[rag_engine] GROQ_API_KEY not set. "
                "Add it to your .env file or environment variables."
            )
        _client = OpenAI(
            api_key=api_key,
            base_url=GROQ_BASE_URL,
        )
        print("[rag_engine] ✅ LLM client ready.")

    print("[rag_engine] ✅ System fully initialized.")


def get_answer(user_input: str, session_id: str, is_followup: bool = False) -> str:
    _ensure_initialized()

    session = memory_manager.get_session(session_id)

    if prompt_manager.is_pricing_query(user_input):
        purchase_resp = prompt_manager.get_purchase_response(user_input)
        if purchase_resp:
            session.record(user_input, purchase_resp, intent="knowledge")
            return purchase_resp
        session.record(user_input, prompt_manager.PRICING_RESPONSE, intent="knowledge")
        return prompt_manager.PRICING_RESPONSE
    

    resolved_query = user_input
    if needs_context_resolution(user_input) and session.last_topic:
        # Only resolve if the last_topic is NOT already present in the query.
        # This prevents double-injection when intent_router already resolved it.
        if session.last_topic.lower() not in user_input.lower():
            resolved_query = resolve_context(user_input, session.last_topic)
            print(f"[rag_engine] Context resolved: '{user_input}' → '{resolved_query}'")

    is_single_fact = prompt_manager.is_single_fact_query(resolved_query)
    if is_single_fact:
        print(f"[rag_engine] Single-fact query detected: '{resolved_query}'")

    try:
        if is_followup:
            retriever = vector_store.get_db().as_retriever(
                search_type="mmr",
                search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.45},
            )
        else:
            retriever = vector_store.get_retriever()
        docs = retriever.invoke(resolved_query)
    except Exception as e:
        print(f"[rag_engine] Retrieval error: {e}")
        return prompt_manager.NO_CONTEXT_RESPONSE
    
    context = "\n\n".join(
        doc.page_content.strip() for doc in docs if doc.page_content.strip()
    )

    if not context:
        session.record(user_input, prompt_manager.NO_CONTEXT_RESPONSE, intent="knowledge")
        return prompt_manager.NO_CONTEXT_RESPONSE

    # ------------------------------------------------------------------
    # Step 4: Pricing-in-context guard
    # ------------------------------------------------------------------
    # context_lower = context.lower()

    # # Hard indicators: actual monetary amounts (e.g. "$500", "inr 10,000", "€99")
    # _currency_amount = re.search(
    #     r"([$€£¥]|inr|usd|eur|gbp)\s*[\d,]+|[\d,]+\s*(inr|usd|eur|gbp)",
    #     context_lower
    # )
    # # Structural indicators: dedicated pricing sections
    # _pricing_section = any(ind in context_lower for ind in [
    #     "price list", "rate card", "pricing table",
    #     "cost breakdown:", "quotation:", "per license",
    #     "pricing details:", "subscription fee",
    # ])

    # if _currency_amount or _pricing_section:
    #     session.record(user_input, prompt_manager.PRICING_RESPONSE, intent="knowledge")
    #     return prompt_manager.PRICING_RESPONSE


    history_text     = session.get_history_text(max_pairs=3)
    topics_discussed = session.topics_as_string()

    prompt = prompt_manager.build_rag_prompt(
        context=context,
        query=resolved_query,
        history=history_text,
        topics_discussed=topics_discussed,
        is_followup=is_followup,
        is_single_fact=is_single_fact,
    )

    try:
        response = _client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are SVA — Softdel Virtual Assistant. "
                        "Follow the instructions in the user message exactly. "
                        "Never reveal pricing. Never add filler phrases."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[rag_engine] LLM call error: {e}")
        return (
            "⚠️ I'm having trouble connecting right now. "
            "Please try again in a moment."
        )

    answer = clean_llm_output(answer)
    answer = _clean_topic_markdown(answer)   
    session.record(user_input, answer, intent="knowledge")

    if session.should_suggest_scheduling() and not is_single_fact:
        answer += prompt_manager.SCHEDULING_NUDGE

    print(f"[rag_engine] Query: '{resolved_query}' | Docs retrieved: {len(docs)}")
    return answer



def _clean_topic_markdown(answer: str) -> str:
    """
    Strip markdown formatting (**bold**, __underline__, *italic*, `code`)
    from the 'You might also be interested in:' topic section.

    LLMs sometimes output **Smart Buildings** or __IoT Solutions__ despite
    being told not to. This ensures topic buttons are always plain text
    so the JS click handler sends clean queries.
    """
    import re as _re
    marker = "You might also be interested in:"
    if marker not in answer:
        return answer

    before, after = answer.split(marker, 1)

    def _strip_md(line):
        # Remove **bold**, __underline__, *italic*, _italic_, `code`
        line = _re.sub(r"[*_`]{1,2}([^*_`\n]+)[*_`]{1,2}", r"\1", line)
        # Remove markdown links [text](url) — keep just the text
        line = _re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", line)
        return line

    cleaned = "\n".join(_strip_md(line) for line in after.splitlines())
    return before + marker + cleaned

def _ensure_initialized():
    """Raise a clear error if initialize() was never called."""
    if _client is None or not vector_store.is_loaded():
        raise RuntimeError(
            "[rag_engine] System not initialized. "
            "Call rag_engine.initialize() at application startup."
        )