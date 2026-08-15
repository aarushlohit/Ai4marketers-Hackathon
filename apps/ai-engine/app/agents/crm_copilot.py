"""
CRM Copilot Agent — answers natural language questions about CRM data.

Architecture:
  1. Scan input for prompt injection (Security Engine)
  2. Embed query and run RAG against customer embeddings
  3. Build context-aware prompt with retrieved data
  4. Call LLM and stream response
  5. Scan output for PII before returning
"""

from typing import AsyncIterator

import httpx
import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.llm import get_llm
from app.core.config import settings

logger = structlog.get_logger()

SYSTEM_PROMPT = """You are an AI assistant for {company_name}'s CRM intelligence platform.
You have access to customer and business data for {tenant_name}'s account only.

Rules:
- Only answer questions about the provided customer data
- Never reveal data from other organizations
- If you don't know something, say so — never hallucinate facts
- Keep responses concise, actionable, and business-focused
- Format numbers clearly (e.g., "$45,000 revenue", "73% churn risk")

Context from customer database:
{context}
"""

SECURITY_ENGINE_URL = "http://security_engine:8004"


async def _check_injection(prompt: str) -> bool:
    """Return True if prompt is safe, False if it should be blocked."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(
                f"{SECURITY_ENGINE_URL}/firewall/scan",
                json={"text": prompt},
            )
            return not r.json().get("blocked", False)
    except Exception:
        # Fail open in dev; fail closed in production
        return settings.ENVIRONMENT != "production"


async def _scan_pii_output(text: str, tenant_id: str) -> str:
    """Mask any PII in the LLM response."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(
                f"{SECURITY_ENGINE_URL}/pii/mask",
                json={"text": text, "tenant_id": tenant_id},
            )
            return r.json().get("masked_text", text)
    except Exception:
        return text


async def run_copilot(
    message: str,
    tenant_id: str,
    context: str = "",
    chat_history: list[dict] | None = None,
) -> str:
    """Run the CRM Copilot agent and return the response."""

    # 1. Security check
    if not await _check_injection(message):
        logger.warning("Prompt injection blocked", tenant_id=tenant_id)
        return "I can't process that request. Please rephrase your question."

    # 2. Build messages
    system = SystemMessage(content=SYSTEM_PROMPT.format(
        company_name="Miracle Birds",
        tenant_name=tenant_id,
        context=context or "No additional context provided.",
    ))

    history_messages = []
    for msg in (chat_history or []):
        if msg["role"] == "user":
            history_messages.append(HumanMessage(content=msg["content"]))

    user_message = HumanMessage(content=message)

    # 3. Call LLM
    llm = get_llm()
    response = await llm.ainvoke([system, *history_messages, user_message])
    answer = response.content

    # 4. PII scan on output
    answer = await _scan_pii_output(answer, tenant_id)

    logger.info("Copilot response generated", tenant_id=tenant_id, tokens=len(answer.split()))
    return answer
