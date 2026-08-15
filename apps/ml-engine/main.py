"""
Miracle Birds — ML Engine
Predictive analytics service: churn, lead scoring, revenue, health score.
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ML Engine starting — loading models")
    from app.core.model_registry import ModelRegistry
    await ModelRegistry.load_all()
    logger.info("ML Engine models loaded")
    yield
    logger.info("ML Engine shutting down")


app = FastAPI(
    title="Miracle Birds ML Engine",
    description="Predictive analytics: churn, lead scoring, revenue, health score",
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
    return JSONResponse({"status": "healthy", "service": "ml-engine"})


# ── Routers ───────────────────────────────────────────────────────────────────
from app.api.predictions import router as predictions_router
from app.api.batch import router as batch_router

app.include_router(predictions_router, prefix="/predict", tags=["Predictions"])
app.include_router(batch_router, prefix="/batch", tags=["Batch"])
