"""
Miracle Birds Phase 3 — Agent Service
Multi-Agent AI Platform with LangGraph orchestration.
"""

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.agents import router as agents_router
from app.api.orchestrator import router as orchestrator_router
from app.api.conversations import router as conversations_router

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Agent Service starting up")
    yield
    logger.info("Agent Service shutting down")


app = FastAPI(
    title=settings.app_name,
    description="Multi-Agent AI Platform — LangGraph orchestration, agent communication, collaboration",
    version=settings.app_version,
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
    return {"status": "healthy", "service": "agent-service", "version": settings.app_version}


app.include_router(agents_router, prefix="/api/v3/agents", tags=["Agents"])
app.include_router(orchestrator_router, prefix="/api/v3/orchestrator", tags=["Orchestrator"])
app.include_router(conversations_router, prefix="/api/v3/conversations", tags=["Conversations"])
