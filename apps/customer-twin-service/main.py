"""
Miracle Birds Phase 3 — Customer Digital Twin Service
Generates and maintains AI Twins for every customer.
"""

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.twins import router as twins_router
from app.api.predictions import router as predictions_router

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Customer Digital Twin Service starting up")
    yield
    logger.info("Customer Digital Twin Service shutting down")


app = FastAPI(
    title="Miracle Birds Customer Digital Twin Service",
    description="AI Twin for every customer — behavior prediction, risk analysis, lifetime value",
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
    return {"status": "healthy", "service": "customer-twin-service", "version": "3.0.0"}


app.include_router(twins_router, prefix="/api/v3/twins", tags=["Customer Twins"])
app.include_router(predictions_router, prefix="/api/v3/twins/predictions", tags=["Twin Predictions"])
