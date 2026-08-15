"""AI Engine embeddings endpoints — generate and store vector embeddings."""

import structlog
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.llm import get_embeddings

router = APIRouter()
logger = structlog.get_logger()


class EmbedRequest(BaseModel):
    texts: list[str]
    tenant_id: str
    source_type: str = "text"


class EmbedResponse(BaseModel):
    embeddings: list[list[float]]
    model: str
    dimensions: int


@router.post("", response_model=EmbedResponse)
async def create_embeddings(payload: EmbedRequest):
    """Generate vector embeddings for a list of texts."""
    embedding_model = get_embeddings()
    vectors = await embedding_model.aembed_documents(payload.texts)
    return EmbedResponse(
        embeddings=vectors,
        model="text-embedding-ada-002",
        dimensions=len(vectors[0]) if vectors else 1536,
    )
