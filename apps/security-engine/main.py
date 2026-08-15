"""
Miracle Birds — Security Engine
Prompt injection firewall, PII detection, threat monitoring.
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Security Engine starting — loading models")
    from app.core.firewall import PromptFirewall
    PromptFirewall.initialize()
    logger.info("Security Engine ready")
    yield
    logger.info("Security Engine shutting down")


app = FastAPI(
    title="Miracle Birds Security Engine",
    description="Prompt injection firewall, PII detection, threat monitoring",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:8001"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", include_in_schema=False)
async def health():
    return JSONResponse({"status": "healthy", "service": "security-engine"})


# ── Routers ───────────────────────────────────────────────────────────────────
from app.api.firewall import router as firewall_router
from app.api.pii import router as pii_router
from app.api.audit import router as audit_router

app.include_router(firewall_router, prefix="/firewall", tags=["Prompt Firewall"])
app.include_router(pii_router, prefix="/pii", tags=["PII Detection"])
app.include_router(audit_router, prefix="/audit", tags=["Audit"])
