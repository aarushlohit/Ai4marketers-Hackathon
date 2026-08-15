"""
Miracle Birds Phase 3 — Simulation Service
AI Strategy Simulator for business scenario modeling.
"""

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.simulations import router as simulations_router
from app.api.scenarios import router as scenarios_router

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Simulation Service starting up")
    yield
    logger.info("Simulation Service shutting down")


app = FastAPI(
    title="Miracle Birds Simulation Service",
    description="AI Strategy Simulator — scenario modeling for pricing, marketing, renewals, upsell, retention",
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
    return {"status": "healthy", "service": "simulation-service", "version": "3.0.0"}


app.include_router(simulations_router, prefix="/api/v3/simulations", tags=["Simulations"])
app.include_router(scenarios_router, prefix="/api/v3/simulations/scenarios", tags=["Scenarios"])
