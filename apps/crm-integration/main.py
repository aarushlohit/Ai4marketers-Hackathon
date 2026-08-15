"""
Miracle Birds — CRM Integration Service
Handles OAuth connections, bi-directional sync, and webhook processing
for Salesforce, Zoho CRM, HubSpot, Microsoft Dynamics 365, and Pipedrive.
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("CRM Integration Service starting")
    yield
    logger.info("CRM Integration Service shutting down")


app = FastAPI(
    title="Miracle Birds CRM Integration Service",
    description="OAuth, bi-directional sync, and webhooks for 5 CRM platforms",
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
    return JSONResponse({"status": "healthy", "service": "crm-integration"})


# ── Routers ───────────────────────────────────────────────────────────────────
from app.api.connections import router as connections_router
from app.api.sync import router as sync_router
from app.api.webhooks import router as webhooks_router

app.include_router(connections_router, tags=["Connections"])
app.include_router(sync_router,        prefix="/sync",     tags=["Sync"])
app.include_router(webhooks_router,    prefix="/webhooks", tags=["Webhooks"])
