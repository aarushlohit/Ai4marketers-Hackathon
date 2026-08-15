"""Memory Service — Compression API.

Compress and summarize memory entries to optimize storage.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.api.memory import _memory_store

router = APIRouter()


class CompressionRequest(BaseModel):
    entry_ids: List[str]
    method: str = "summary"  # summary | deduplicate | prune
    max_tokens: int = 500


class CompressionResult(BaseModel):
    original_count: int
    compressed_count: int
    compression_ratio: float
    entries_affected: List[str]


@router.post("/compact", response_model=CompressionResult)
async def compress_memories(request: CompressionRequest):
    """Compress memory entries by summarizing or deduplicating."""
    affected = []
    compressed_count = 0
    
    for eid in request.entry_ids:
        if eid in _memory_store:
            entry = _memory_store[eid]
            content = entry.get("content", {})
            
            if request.method == "summary" and isinstance(content, dict):
                # Truncate long content (in production: use LLM for summarization)
                content_str = str(content)
                if len(content_str) > request.max_tokens:
                    entry["content"]["_compressed"] = True
                    entry["content"]["_original_length"] = len(content_str)
                    entry["content"]["_summary"] = content_str[:request.max_tokens] + "..."
                    compressed_count += 1
            
            elif request.method == "deduplicate":
                entry["content"]["_deduplicated"] = True
                compressed_count += 1
            
            affected.append(eid)
    
    return CompressionResult(
        original_count=len(request.entry_ids),
        compressed_count=compressed_count,
        compression_ratio=compressed_count / max(len(request.entry_ids), 1),
        entries_affected=affected,
    )


@router.post("/prune", response_model=CompressionResult)
async def prune_memories(
    older_than_days: int = 30,
    min_importance: float = 0.3,
):
    """Remove low-importance memories older than specified days."""
    cutoff = datetime.utcnow() - timedelta(days=older_than_days)
    affected = []
    
    for eid, entry in list(_memory_store.items()):
        created_at = entry.get("created_at", "")
        importance = entry.get("importance_score", 0)
        
        try:
            created_dt = datetime.fromisoformat(created_at)
            if created_dt < cutoff and importance < min_importance:
                del _memory_store[eid]
                affected.append(eid)
        except (ValueError, TypeError):
            pass
    
    return CompressionResult(
        original_count=len(affected),
        compressed_count=len(affected),
        compression_ratio=1.0,
        entries_affected=affected,
    )
