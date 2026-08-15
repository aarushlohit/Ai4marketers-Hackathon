"""AI Copilot endpoints — powered by centralized AI engine with CRM guardrails."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser, get_current_user
from app.core.database import get_db
from app.core.ai_engine import crm_chat, FREE_MODEL

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    context: dict | None = None
    model: str | None = None


@router.post("/chat")
async def chat(
    payload: ChatRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Send a message to the AI CRM Copilot.
    - Guardrails block non-CRM queries
    - Live DB context injected automatically
    - Powered by DeepSeek V4 Flash Free with smart fallback
    """
    response = await crm_chat(
        user_message=payload.message,
        tenant_id=user.tenant_id,
        db=db,
        model=payload.model,
    )
    return {
        "response": response,
        "conversation_id": payload.conversation_id or "default",
        "model": payload.model or FREE_MODEL,
    }


@router.get("/conversations")
async def list_conversations(user: Annotated[CurrentUser, Depends(get_current_user)]):
    """List all Copilot conversations for the current user."""
    return {
        "conversations": [
            {"id": "1", "title": "Churn Analysis", "updated_at": "2026-07-18T10:00:00Z"},
            {"id": "2", "title": "Revenue Forecast Q3", "updated_at": "2026-07-17T15:30:00Z"},
            {"id": "3", "title": "Hot Lead Review", "updated_at": "2026-07-16T09:00:00Z"},
        ]
    }
