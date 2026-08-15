"""
Miracle Birds Phase 3 — Memory Service
Enterprise Memory with pgvector semantic storage.
"""

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.memory import router as memory_router
from app.api.retrieval import router as retrieval_router
from app.api.compression import router as compression_router

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Memory Service starting up")
    yield
    logger.info("Memory Service shutting down")


app = FastAPI(
    title="Miracle Birds Memory Service",
    description="Enterprise Memory — pgvector semantic storage, retrieval, ranking, compression, expiration",
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
    return {"status": "healthy", "service": "memory-service", "version": "3.0.0"}


app.include_router(memory_router, prefix="/api/v3/memory", tags=["Memory"])
app.include_router(retrieval_router, prefix="/api/v3/retrieval", tags=["Retrieval"])
app.include_router(compression_router, prefix="/api/v3/compression", tags=["Compression"])
