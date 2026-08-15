"""Knowledge Service — Edges API.

Edge Types: HAS_DEAL, HAS_MEETING, HAS_ACTIVITY, SENT_EMAIL, 
HAS_RECOMMENDATION, BELONGS_TO, PARTICIPATED_IN, LED_TO, HAS_OUTCOME
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from app.api.nodes import _nodes_store

router = APIRouter()

# In-memory store
_edges_store: Dict[str, Dict[str, Any]] = {}

VALID_EDGE_TYPES = [
    "HAS_DEAL", "HAS_MEETING", "HAS_ACTIVITY", "SENT_EMAIL",
    "HAS_RECOMMENDATION", "BELONGS_TO", "PARTICIPATED_IN",
    "LED_TO", "HAS_OUTCOME", "CONTACTED", "ASSIGNED_TO",
    "CREATED_BY", "MENTIONED_IN", "RELATED_TO", "DEPENDS_ON",
]


class KnowledgeEdge(BaseModel):
    id: str = ""
    tenant_id: str = "00000000-0000-0000-0000-000000000001"
    source_node_id: str
    target_node_id: str
    edge_type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    weight: float = 1.0
    created_at: str = ""


@router.post("", response_model=KnowledgeEdge)
async def create_edge(edge: KnowledgeEdge):
    """Create a new knowledge graph edge."""
    if edge.edge_type not in VALID_EDGE_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid edge type. Must be one of: {', '.join(VALID_EDGE_TYPES)}")
    
    if edge.source_node_id not in _nodes_store:
        raise HTTPException(status_code=404, detail=f"Source node {edge.source_node_id} not found")
    if edge.target_node_id not in _nodes_store:
        raise HTTPException(status_code=404, detail=f"Target node {edge.target_node_id} not found")
    
    edge_id = str(uuid.uuid4())
    edge.id = edge_id
    edge.created_at = datetime.utcnow().isoformat()
    
    _edges_store[edge_id] = edge.model_dump()
    return edge


@router.get("/{edge_id}", response_model=KnowledgeEdge)
async def get_edge(edge_id: str):
    """Get a knowledge graph edge by ID."""
    if edge_id not in _edges_store:
        raise HTTPException(status_code=404, detail="Edge not found")
    return _edges_store[edge_id]


@router.get("", response_model=List[KnowledgeEdge])
async def list_edges(
    source_node_id: Optional[str] = None,
    target_node_id: Optional[str] = None,
    edge_type: Optional[str] = None,
):
    """List edges with optional filters."""
    edges = list(_edges_store.values())
    
    if source_node_id:
        edges = [e for e in edges if e["source_node_id"] == source_node_id]
    if target_node_id:
        edges = [e for e in edges if e["target_node_id"] == target_node_id]
    if edge_type:
        edges = [e for e in edges if e["edge_type"] == edge_type]
    
    return edges


@router.delete("/{edge_id}")
async def delete_edge(edge_id: str):
    """Delete an edge."""
    if edge_id not in _edges_store:
        raise HTTPException(status_code=404, detail="Edge not found")
    del _edges_store[edge_id]
    return {"status": "success", "message": f"Edge {edge_id} deleted"}
