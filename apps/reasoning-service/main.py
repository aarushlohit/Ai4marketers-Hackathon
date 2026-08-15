"""
Miracle Birds Phase 3 — Reasoning Service
Enterprise Reasoning Engine with pipeline-based root cause analysis.
"""

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.pipelines import router as pipelines_router
from app.api.reason import router as reason_router

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Reasoning Service starting up")
    yield
    logger.info("Reasoning Service shutting down")


app = FastAPI(
    title="Miracle Birds Reasoning Service",
    description="Enterprise Reasoning Engine — root cause analysis, evidence-based reasoning, multi-step pipelines",
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
    return {"status": "healthy", "service": "reasoning-service", "version": "3.0.0"}


app.include_router(pipelines_router, prefix="/api/v3/reasoning/pipelines", tags=["Reasoning Pipelines"])
app.include_router(reason_router, prefix="/api/v3/reasoning", tags=["Reasoning"])
