"""Security Engine — PII Detection & Masking endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.pii_detector import PIIDetector

router = APIRouter()


class PIIRequest(BaseModel):
    text: str
    tenant_id: str | None = None


class DetectResponse(BaseModel):
    has_pii: bool
    findings: list[dict]
    count: int


class MaskResponse(BaseModel):
    original_length: int
    masked_text: str
    has_pii: bool


@router.post("/detect", response_model=DetectResponse)
async def detect_pii(payload: PIIRequest):
    """Detect PII entities in text."""
    findings = PIIDetector.detect(payload.text)
    return DetectResponse(has_pii=len(findings) > 0, findings=findings, count=len(findings))


@router.post("/mask", response_model=MaskResponse)
async def mask_pii(payload: PIIRequest):
    """Detect and mask all PII in text."""
    has_pii = PIIDetector.contains_pii(payload.text)
    masked = PIIDetector.mask(payload.text)
    return MaskResponse(
        original_length=len(payload.text),
        masked_text=masked,
        has_pii=has_pii,
    )
