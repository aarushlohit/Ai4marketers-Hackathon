"""Security Engine — Prompt Injection Firewall endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.firewall import PromptFirewall

router = APIRouter()


class ScanRequest(BaseModel):
    text: str
    tenant_id: str | None = None


class ScanResponse(BaseModel):
    blocked: bool
    reason: str | None
    confidence: float


@router.post("/scan", response_model=ScanResponse)
async def scan_prompt(payload: ScanRequest):
    """Scan text for prompt injection attacks."""
    result = PromptFirewall.scan(payload.text)
    return ScanResponse(**result)
