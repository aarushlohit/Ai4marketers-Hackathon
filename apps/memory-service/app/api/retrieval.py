"""Memory Service — Retrieval API.

Semantic retrieval with pgvector similarity search and ranking.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import uuid

from app.api.memory import _memory_store

router = APIRouter()


class RetrievalQuery(BaseModel):
    query: str
    memory_types: Optional[List[str]] = None
    customer_id: Optional[str] = None
    agent_id: Optional[str] = None
    top_k: int = 10
    min_score: float = 0.0
    include_expired: bool = False


class RetrievalResult(BaseModel):
    id: str
    memory_type: str
    content: Dict[str, Any]
    relevance_score: float
    importance_score: float
    tags: List[str]
    created_at: str


class RetrievalResponse(BaseModel):
    query: str
    results: List[RetrievalResult]
    total_found: int
    average_score: float


@router.post("/semantic", response_model=RetrievalResponse)
async def semantic_retrieval(query: RetrievalQuery):
    """Semantic search using embeddings (mock with text matching)."""
    entries = list(_memory_store.values())
    
    if query.memory_types:
        entries = [e for e in entries if e["memory_type"] in query.memory_types]
    if query.customer_id:
        entries = [e for e in entries if e.get("customer_id") == query.customer_id]
    if query.agent_id:
        entries = [e for e in entries if e.get("agent_id") == query.agent_id]
    
    # Score by text similarity (in production: vector similarity)
    query_lower = query.query.lower()
    scored = []
    for entry in entries:
        content_str = str(entry.get("content", {})).lower()
        tags = [t.lower() for t in entry.get("tags", [])]
        
        # Simple scoring
        score = 0.0
        if query_lower in content_str:
            score += 0.6
        if any(query_lower in tag for tag in tags):
            score += 0.3
        score += entry.get("importance_score", 0) * 0.1
        
        if score >= query.min_score:
            scored.append((score, entry))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    top_results = scored[:query.top_k]
    
    results = [
        RetrievalResult(
            id=e["id"],
            memory_type=e["memory_type"],
            content=e.get("content", {}),
            relevance_score=round(score, 3),
            importance_score=e.get("importance_score", 0),
            tags=e.get("tags", []),
            created_at=e.get("created_at", ""),
        )
        for score, e in top_results
    ]
    
    avg_score = sum(r.relevance_score for r in results) / max(len(results), 1)
    
    return RetrievalResponse(
        query=query.query,
        results=results,
        total_found=len(results),
        average_score=round(avg_score, 3),
    )


@router.post("/hybrid")
async def hybrid_retrieval(query: RetrievalQuery):
    """Hybrid retrieval combining semantic and keyword search."""
    semantic_results = await semantic_retrieval(query)
    
    # Boost results with exact keyword matches
    keyword_terms = query.query.lower().split()
    boosted = []
    for result in semantic_results.results:
        boost = 0.0
        content_str = str(result.content).lower()
        for term in keyword_terms:
            if term in content_str:
                boost += 0.1
        result.relevance_score = min(1.0, result.relevance_score + boost)
        boosted.append(result)
    
    boosted.sort(key=lambda r: r.relevance_score, reverse=True)
    
    return RetrievalResponse(
        query=query.query,
        results=boosted,
        total_found=len(boosted),
        average_score=round(
            sum(r.relevance_score for r in boosted) / max(len(boosted), 1), 3
        ),
    )


@router.post("/context/{context_id}")
async def get_context(context_id: str, depth: int = 1):
    """Get context around a specific memory entry (related memories)."""
    # Find the target entry
    if context_id not in _memory_store:
        raise HTTPException(status_code=404, detail="Memory entry not found")
    
    target = _memory_store[context_id]
    related = []
    
    # Find related entries by tags and customer_id
    target_tags = set(target.get("tags", []))
    target_customer = target.get("customer_id")
    
    for eid, entry in _memory_store.items():
        if eid == context_id:
            continue
        
        relevance = 0.0
        entry_tags = set(entry.get("tags", []))
        common_tags = target_tags & entry_tags
        relevance += len(common_tags) * 0.2
        
        if entry.get("customer_id") and entry["customer_id"] == target_customer:
            relevance += 0.3
        
        if relevance > 0:
            related.append({
                "id": eid,
                "memory_type": entry["memory_type"],
                "content": entry.get("content", {}),
                "relevance": round(relevance, 2),
                "created_at": entry.get("created_at", ""),
            })
    
    related.sort(key=lambda r: r["relevance"], reverse=True)
    
    return {
        "context_id": context_id,
        "target": {
            "id": context_id,
            "memory_type": target["memory_type"],
            "content": target.get("content", {}),
            "created_at": target.get("created_at", ""),
        },
        "related_entries": related[:10 * depth],
        "total_related": len(related),
    }
