"""
Miracle Birds — Workflow Engine
Automated workflow execution triggered by AI predictions and CRM events.
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Workflow Engine starting")
    yield
    logger.info("Workflow Engine shutting down")


app = FastAPI(
    title="Miracle Birds Workflow Engine",
    description="Automated workflow execution triggered by AI events",
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
    return JSONResponse({"status": "healthy", "service": "workflow-engine"})


# ── Routers ───────────────────────────────────────────────────────────────────
from app.api.workflows import router as workflows_router
from app.api.executions import router as executions_router

app.include_router(workflows_router, prefix="/workflows", tags=["Workflows"])
app.include_router(executions_router, prefix="/executions", tags=["Executions"])
