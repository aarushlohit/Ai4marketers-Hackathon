"""Search Service — Embeddings API.

Generate and search vector embeddings for semantic understanding.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import math

router = APIRouter()

# In-memory embedding store
_embeddings_store: Dict[str, Dict[str, Any]] = {}


class EmbeddingRequest(BaseModel):
    text: str
    source_type: Optional[str] = None
    source_id: Optional[str] = None
    tenant_id: str = "00000000-0000-0000-0000-000000000001"


class EmbeddingResponse(BaseModel):
    id: str
    text_preview: str
    embedding: List[float]
    dimension: int
    source_type: Optional[str] = None
    source_id: Optional[str] = None
    created_at: str


class SimilaritySearchRequest(BaseModel):
    embedding: List[float]
    source_type: Optional[str] = None
    limit: int = 10
    min_score: float = 0.0


class SimilarityResult(BaseModel):
    id: str
    text_preview: str
    source_type: Optional[str]
    similarity_score: float


@router.post("/generate", response_model=EmbeddingResponse)
async def generate_embedding(request: EmbeddingRequest):
    """Generate a vector embedding for text."""
    emb_id = str(uuid.uuid4())
    
    # Mock embedding generation (in production: call OpenAI/text-embedding-3-small)
    embedding = _mock_generate_embedding(request.text)
    
    entry = {
        "id": emb_id,
        "text_preview": request.text[:100],
        "embedding": embedding,
        "dimension": 1536,
        "source_type": request.source_type,
        "source_id": request.source_id,
        "tenant_id": request.tenant_id,
        "created_at": datetime.utcnow().isoformat(),
    }
    _embeddings_store[emb_id] = entry
    
    return EmbeddingResponse(**entry)


@router.post("/similarity", response_model=List[SimilarityResult])
async def search_similar(request: SimilaritySearchRequest):
    """Find similar embeddings by cosine similarity."""
    if len(request.embedding) != 1536:
        raise HTTPException(status_code=400, detail="Embedding must be 1536 dimensions")
    
    results = []
    for eid, entry in _embeddings_store.items():
        if request.source_type and entry.get("source_type") != request.source_type:
            continue
        
        similarity = _cosine_similarity(request.embedding, entry["embedding"])
        if similarity >= request.min_score:
            results.append(SimilarityResult(
                id=eid,
                text_preview=entry["text_preview"],
                source_type=entry.get("source_type"),
                similarity_score=round(similarity, 4),
            ))
    
    results.sort(key=lambda r: r.similarity_score, reverse=True)
    return results[:request.limit]


@router.delete("/{embedding_id}")
async def delete_embedding(embedding_id: str):
    """Delete an embedding."""
    if embedding_id not in _embeddings_store:
        raise HTTPException(status_code=404, detail="Embedding not found")
    del _embeddings_store[embedding_id]
    return {"status": "success", "message": f"Embedding {embedding_id} deleted"}


def _mock_generate_embedding(text: str) -> List[float]:
    """Generate a mock embedding vector. Replace with actual model in production."""
    import hashlib
    
    # Use hash to create deterministic mock embeddings
    hash_obj = hashlib.sha256(text.encode())
    hash_bytes = hash_obj.digest()
    
    embedding = []
    for i in range(1536):
        # Use hash bytes cyclically to generate pseudo-random values
        val = (hash_bytes[i % 32] * (i + 1)) / 255.0
        embedding.append((val - 0.5) * 2)  # Normalize to [-1, 1]
    
    # Normalize the vector
    norm = math.sqrt(sum(v * v for v in embedding))
    if norm > 0:
        embedding = [v / norm for v in embedding]
    
    return embedding


def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)
