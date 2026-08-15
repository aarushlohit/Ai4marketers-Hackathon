"""AI Engine chat endpoints — Copilot conversations."""

import uuid
from typing import Annotated

import redis.asyncio as aioredis
import structlog
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import BaseModel

from app.agents.crm_copilot import run_copilot
from app.core.config import settings

router = APIRouter()
logger = structlog.get_logger()


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    tenant_id: str
    user_id: str
    context: dict = {}


class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    suggestions: list[str] = []


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    """Process a chat message and return a Copilot response."""
    conversation_id = payload.conversation_id or str(uuid.uuid4())

    # Load conversation history from Redis
    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    history_key = f"conv:{payload.tenant_id}:{conversation_id}"
    raw_history = await redis.lrange(history_key, 0, 19)  # last 20 messages

    history = []
    for item in raw_history:
        import json
        try:
            history.append(json.loads(item))
        except Exception:
            pass

    # Run copilot
    response = await run_copilot(
        message=payload.message,
        tenant_id=payload.tenant_id,
        context=str(payload.context),
        chat_history=history,
    )

    # Persist messages to Redis
    import json
    await redis.rpush(history_key, json.dumps({"role": "user", "content": payload.message}))
    await redis.rpush(history_key, json.dumps({"role": "assistant", "content": response}))
    await redis.expire(history_key, settings.CONVERSATION_TTL)
    await redis.aclose()

    return ChatResponse(
        message=response,
        conversation_id=conversation_id,
        suggestions=[
            "Tell me more about this customer",
            "What actions do you recommend?",
            "Show me the churn risk details",
        ],
    )


@router.post("/conversations")
async def list_conversations(payload: dict = Body(...)):
    """List recent conversations for a user (stub — extend with DB query)."""
    return {"conversations": []}
