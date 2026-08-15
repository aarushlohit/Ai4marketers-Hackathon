"""Client for the Security Engine (prompt firewall + PII detection)."""

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger()


async def scan_prompt_injection(text: str, tenant_id: str | None = None) -> dict:
    """Call security engine firewall. Falls back to local pattern check."""
    if not settings.SECURITY_ENGINE_URL:
        return _local_scan(text)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{settings.SECURITY_ENGINE_URL.rstrip('/')}/firewall/scan",
                json={"text": text, "tenant_id": tenant_id},
            )
            response.raise_for_status()
            return response.json()
    except Exception as exc:
        logger.warning("security_engine_unavailable", error=str(exc))
        return _local_scan(text)


def _local_scan(text: str) -> dict:
    patterns = [
        "ignore previous instructions",
        "forget your system prompt",
        "jailbreak",
        "developer mode",
        "reveal your instructions",
    ]
    lower = text.lower()
    for pattern in patterns:
        if pattern in lower:
            return {"blocked": True, "reason": "pattern_match", "confidence": 1.0}
    return {"blocked": False, "reason": None, "confidence": 0.0}
