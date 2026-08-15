from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Miracle Birds Phase 2 API",
    description="Adaptive Intelligence Platform API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.v2 import agents, graph, memory, workflows  # noqa: E402


@app.get("/")
def read_root():
    return {"message": "Miracle Birds Phase 2 API is running"}


@app.get("/api/v2/health")
def health_check():
    return {"status": "ok", "version": "2.0.0"}


app.include_router(agents.router, prefix="/api/v2/agents", tags=["Agents"])
app.include_router(graph.router, prefix="/api/v2/graph", tags=["Knowledge Graph"])
app.include_router(memory.router, prefix="/api/v2/memory", tags=["Enterprise Memory"])
app.include_router(workflows.router, prefix="/api/v2/workflows", tags=["Workflows"])
