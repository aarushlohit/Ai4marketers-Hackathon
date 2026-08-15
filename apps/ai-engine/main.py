"""
Miracle Birds — AI Engine
LLM orchestration service: Copilot, RAG, embeddings, agents.
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AI Engine starting up")
    # Pre-load embedding model, warm up LLM connection
    yield
    logger.info("AI Engine shutting down")


app = FastAPI(
    title="Miracle Birds AI Engine",
    description="LLM orchestration: Copilot, RAG, agents, embeddings",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", include_in_schema=False)
async def health():
    return JSONResponse({"status": "healthy", "service": "ai-engine"})


# ── Routers ───────────────────────────────────────────────────────────────────
from app.api.chat import router as chat_router
from app.api.embeddings import router as embeddings_router
from app.api.meetings import router as meetings_router
from app.api.recommendations import router as recommendations_router
from app.api.executive import router as executive_router

app.include_router(chat_router, prefix="/chat", tags=["Copilot"])
app.include_router(embeddings_router, prefix="/embeddings", tags=["Embeddings"])
app.include_router(meetings_router, prefix="/meetings", tags=["Meetings"])
app.include_router(recommendations_router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(executive_router, prefix="/executive", tags=["Executive"])
