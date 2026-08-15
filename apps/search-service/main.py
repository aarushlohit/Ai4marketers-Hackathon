"""
Miracle Birds Phase 3 — Search Service
Semantic Enterprise Search across customers, meetings, emails, activities, recommendations, knowledge graph.
"""

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.search import router as search_router
from app.api.embeddings import router as embeddings_router

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Search Service starting up")
    yield
    logger.info("Search Service shutting down")


app = FastAPI(
    title="Miracle Birds Search Service",
    description="Semantic Enterprise Search — cross-entity ranked results with embeddings",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "search-service", "version": "3.0.0"}


app.include_router(search_router, prefix="/api/v3/search", tags=["Search"])
app.include_router(embeddings_router, prefix="/api/v3/embeddings", tags=["Embeddings"])
