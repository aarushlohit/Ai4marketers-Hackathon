"""Agent Service — Agent Conversations API.

Tracks inter-agent communication and conversation history.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter()

# In-memory conversation store
_conversations: dict = {}


class ConversationMessage(BaseModel):
    id: str = ""
    from_agent: str
    to_agent: str
    message_type: str = "query"  # query | response | broadcast | delegate
    content: dict = {}
    session_id: str = ""
    status: str = "pending"
    timestamp: str = ""


class ConversationSession(BaseModel):
    id: str
    title: str = ""
    messages: List[ConversationMessage] = []
    created_at: str = ""
    updated_at: str = ""


@router.get("/sessions", response_model=List[ConversationSession])
async def list_sessions(limit: int = 20):
    """List recent conversation sessions."""
    sessions = list(_conversations.values())
    sessions.sort(key=lambda s: s.updated_at, reverse=True)
    return sessions[:limit]


@router.post("/sessions", response_model=ConversationSession)
async def create_session():
    """Create a new conversation session."""
    session_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    session = ConversationSession(
        id=session_id,
        title=f"Session {session_id[:8]}",
        created_at=now,
        updated_at=now,
    )
    _conversations[session_id] = session
    return session


@router.get("/sessions/{session_id}", response_model=ConversationSession)
async def get_session(session_id: str):
    """Get a conversation session by ID."""
    if session_id not in _conversations:
        raise HTTPException(status_code=404, detail="Session not found")
    return _conversations[session_id]


@router.post("/sessions/{session_id}/messages", response_model=ConversationMessage)
async def add_message(session_id: str, message: ConversationMessage):
    """Add a message to a conversation session."""
    if session_id not in _conversations:
        raise HTTPException(status_code=404, detail="Session not found")

    msg_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    msg = ConversationMessage(
        id=msg_id,
        from_agent=message.from_agent,
        to_agent=message.to_agent,
        message_type=message.message_type,
        content=message.content,
        session_id=session_id,
        status="sent",
        timestamp=now,
    )
    _conversations[session_id].messages.append(msg)
    _conversations[session_id].updated_at = now
    return msg


@router.get("/sessions/{session_id}/messages", response_model=List[ConversationMessage])
async def get_messages(session_id: str, agent_type: Optional[str] = None):
    """Get messages from a session, optionally filtered by agent."""
    if session_id not in _conversations:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = _conversations[session_id].messages
    if agent_type:
        messages = [m for m in messages if m.from_agent == agent_type or m.to_agent == agent_type]
    return messages
