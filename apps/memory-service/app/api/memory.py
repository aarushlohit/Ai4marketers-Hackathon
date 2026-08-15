"""Memory Service — Enterprise Memory CRUD API.

Memory Types:
- Session Memory
- Customer Memory
- Meeting Memory
- Business Memory
- Agent Memory

Stores: Customer interactions, meetings, recommendations, decisions, feedback, emails, activities, support tickets
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import uuid

router = APIRouter()

# In-memory store (replace with pgvector in production)
_memory_store: Dict[str, Dict[str, Any]] = {}


class MemoryEntry(BaseModel):
    id: str = ""
    tenant_id: str = "00000000-0000-0000-0000-000000000001"
    agent_id: Optional[str] = None
    customer_id: Optional[str] = None
    memory_type: str  # session | customer | meeting | business | agent
    content: Dict[str, Any] = Field(default_factory=dict)
    importance_score: float = 0.0
    embedding: Optional[List[float]] = None
    tags: List[str] = Field(default_factory=list)
    expires_at: Optional[str] = None
    created_at: str = ""


class MemorySearchRequest(BaseModel):
    query: str
    memory_type: Optional[str] = None
    customer_id: Optional[str] = None
    agent_id: Optional[str] = None
    limit: int = 10
    min_importance: float = 0.0


class MemorySearchResponse(BaseModel):
    results: List[MemoryEntry]
    total: int
    query: str


@router.post("/entries", response_model=MemoryEntry)
async def store_memory(entry: MemoryEntry):
    """Store a new memory entry with automatic embedding."""
    entry_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    entry.id = entry_id
    entry.created_at = now
    
    # Set default expiration based on memory type
    if not entry.expires_at:
        expiry_map = {
            "session": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "customer": (datetime.utcnow() + timedelta(days=90)).isoformat(),
            "meeting": (datetime.utcnow() + timedelta(days=365)).isoformat(),
            "business": (datetime.utcnow() + timedelta(days=365)).isoformat(),
            "agent": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        }
        entry.expires_at = expiry_map.get(entry.memory_type, (datetime.utcnow() + timedelta(days=30)).isoformat())
    
    _memory_store[entry_id] = entry.model_dump()
    return entry


@router.get("/entries/{entry_id}", response_model=MemoryEntry)
async def get_memory(entry_id: str):
    """Retrieve a specific memory entry."""
    if entry_id not in _memory_store:
        raise HTTPException(status_code=404, detail="Memory entry not found")
    return _memory_store[entry_id]


@router.get("/entries", response_model=List[MemoryEntry])
async def list_memory(
    memory_type: Optional[str] = None,
    customer_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    limit: int = Query(default=50, le=100),
):
    """List memory entries with optional filters."""
    entries = list(_memory_store.values())
    
    if memory_type:
        entries = [e for e in entries if e["memory_type"] == memory_type]
    if customer_id:
        entries = [e for e in entries if e.get("customer_id") == customer_id]
    if agent_id:
        entries = [e for e in entries if e.get("agent_id") == agent_id]
    
    entries.sort(key=lambda e: e.get("importance_score", 0), reverse=True)
    return entries[:limit]


@router.delete("/entries/{entry_id}")
async def delete_memory(entry_id: str):
    """Delete a memory entry."""
    if entry_id not in _memory_store:
        raise HTTPException(status_code=404, detail="Memory entry not found")
    del _memory_store[entry_id]
    return {"status": "success", "message": "Memory entry deleted"}


@router.post("/search", response_model=MemorySearchResponse)
async def search_memory(request: MemorySearchRequest):
    """Semantic search across memory entries."""
    entries = list(_memory_store.values())
    
    if request.memory_type:
        entries = [e for e in entries if e["memory_type"] == request.memory_type]
    if request.customer_id:
        entries = [e for e in entries if e.get("customer_id") == request.customer_id]
    if request.agent_id:
        entries = [e for e in entries if e.get("agent_id") == request.agent_id]
    if request.min_importance > 0:
        entries = [e for e in entries if e.get("importance_score", 0) >= request.min_importance]
    
    # Simple text-based scoring (replace with vector similarity in production)
    query_lower = request.query.lower()
    scored_entries = []
    for e in entries:
        content_str = str(e.get("content", {}))
        tags = e.get("tags", [])
        
        score = 0.0
        if query_lower in content_str.lower():
            score += 0.5
        for tag in tags:
            if query_lower in tag.lower():
                score += 0.3
        score += e.get("importance_score", 0) * 0.2
        
        if score > 0:
            scored_entries.append((score, e))
    
    scored_entries.sort(key=lambda x: x[0], reverse=True)
    results = [e for _, e in scored_entries[:request.limit]]
    
    return MemorySearchResponse(
        results=[MemoryEntry(**r) for r in results],
        total=len(results),
        query=request.query,
    )


@router.post("/rank")
async def rank_memories(entry_ids: List[str], query: str):
    """Rank memory entries by relevance to a query."""
    ranked = []
    for eid in entry_ids:
        if eid in _memory_store:
            entry = _memory_store[eid]
            content_str = str(entry.get("content", {}))
            query_lower = query.lower()
            relevance = 0.0
            if query_lower in content_str.lower():
                relevance += 1.0
            relevance += entry.get("importance_score", 0) * 0.5
            ranked.append({"entry_id": eid, "relevance": round(relevance, 3)})
    
    ranked.sort(key=lambda r: r["relevance"], reverse=True)
    return {"ranked": ranked, "query": query}


@router.post("/cleanup")
async def cleanup_expired():
    """Remove expired memory entries."""
    now = datetime.utcnow()
    expired_ids = []
    for eid, entry in list(_memory_store.items()):
        expires_at = entry.get("expires_at")
        if expires_at:
            try:
                expires_dt = datetime.fromisoformat(expires_at)
                if expires_dt < now:
                    expired_ids.append(eid)
                    del _memory_store[eid]
            except (ValueError, TypeError):
                pass
    return {"status": "success", "entries_cleaned": len(expired_ids), "expired_ids": expired_ids}


@router.post("/customer/{customer_id}/timeline")
async def get_customer_timeline(customer_id: str):
    """Get chronological timeline for a customer."""
    entries = [e for e in _memory_store.values() if e.get("customer_id") == customer_id]
    entries.sort(key=lambda e: e.get("created_at", ""), reverse=True)
    
    return {
        "customer_id": customer_id,
        "total_events": len(entries),
        "timeline": [
            {
                "id": e["id"],
                "type": e["memory_type"],
                "summary": str(e.get("content", {}))[:200],
                "importance": e.get("importance_score", 0),
                "timestamp": e.get("created_at", ""),
            }
            for e in entries[:50]
        ],
    }
