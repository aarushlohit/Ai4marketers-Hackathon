"""
Miracle Birds Phase 3 — Knowledge Service
Enterprise Knowledge Graph for relationship discovery and graph traversal.
"""

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.nodes import router as nodes_router
from app.api.edges import router as edges_router
from app.api.traversal import router as traversal_router
from app.api.discovery import router as discovery_router

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Knowledge Service starting up")
    yield
    logger.info("Knowledge Service shutting down")


app = FastAPI(
    title="Miracle Birds Knowledge Service",
    description="Enterprise Knowledge Graph — nodes, edges, traversal, semantic retrieval, GraphRAG-ready",
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
    return {"status": "healthy", "service": "knowledge-service", "version": "3.0.0"}


app.include_router(nodes_router, prefix="/api/v3/knowledge/nodes", tags=["Knowledge Nodes"])
app.include_router(edges_router, prefix="/api/v3/knowledge/edges", tags=["Knowledge Edges"])
app.include_router(traversal_router, prefix="/api/v3/knowledge/traversal", tags=["Graph Traversal"])
app.include_router(discovery_router, prefix="/api/v3/knowledge/discovery", tags=["Relationship Discovery"])
