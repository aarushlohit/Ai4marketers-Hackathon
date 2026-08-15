"""
Miracle Birds Phase 3 — Executive Service
Executive Boardroom for multi-agent executive reporting.
"""

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.reports import router as reports_router
from app.api.insights import router as insights_router

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Executive Service starting up")
    yield
    logger.info("Executive Service shutting down")


app = FastAPI(
    title="Miracle Birds Executive Service",
    description="Executive Boardroom — multi-agent reporting, insights, charts, root cause, recommendations",
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
    return {"status": "healthy", "service": "executive-service", "version": "3.0.0"}


app.include_router(reports_router, prefix="/api/v3/executive/reports", tags=["Executive Reports"])
app.include_router(insights_router, prefix="/api/v3/executive/insights", tags=["Executive Insights"])
