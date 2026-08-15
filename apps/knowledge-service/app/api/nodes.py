"""Knowledge Service — Nodes API.

Knowledge Graph Node Types:
Customer, Organization, Lead, Deal, Meeting, Employee, Activity, Email, Recommendation, Workflow
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

router = APIRouter()

# In-memory store (replace with PostgreSQL + pgvector in production)
_nodes_store: Dict[str, Dict[str, Any]] = {}

VALID_NODE_TYPES = [
    "Customer", "Organization", "Lead", "Deal", "Meeting",
    "Employee", "Activity", "Email", "Recommendation", "Workflow",
]


class KnowledgeNode(BaseModel):
    id: str = ""
    tenant_id: str = "00000000-0000-0000-0000-000000000001"
    node_type: str
    external_id: Optional[str] = None
    name: str
    labels: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: str = ""
    updated_at: str = ""


@router.post("", response_model=KnowledgeNode)
async def create_node(node: KnowledgeNode):
    """Create a new knowledge graph node."""
    if node.node_type not in VALID_NODE_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid node type. Must be one of: {', '.join(VALID_NODE_TYPES)}")
    
    node_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    node.id = node_id
    node.created_at = now
    node.updated_at = now
    
    _nodes_store[node_id] = node.model_dump()
    return node


@router.get("/{node_id}", response_model=KnowledgeNode)
async def get_node(node_id: str):
    """Get a knowledge graph node by ID."""
    if node_id not in _nodes_store:
        raise HTTPException(status_code=404, detail="Node not found")
    return _nodes_store[node_id]


@router.get("", response_model=List[KnowledgeNode])
async def list_nodes(
    node_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(default=50, le=200),
):
    """List nodes with optional type filter and text search."""
    nodes = list(_nodes_store.values())
    
    if node_type:
        nodes = [n for n in nodes if n["node_type"] == node_type]
    if search:
        search_lower = search.lower()
        nodes = [n for n in nodes if search_lower in n["name"].lower() or search_lower in str(n.get("properties", {})).lower()]
    
    return nodes[:limit]


@router.put("/{node_id}", response_model=KnowledgeNode)
async def update_node(node_id: str, node: KnowledgeNode):
    """Update a knowledge graph node."""
    if node_id not in _nodes_store:
        raise HTTPException(status_code=404, detail="Node not found")
    
    existing = _nodes_store[node_id]
    existing["name"] = node.name
    existing["node_type"] = node.node_type
    existing["labels"] = node.labels
    existing["properties"] = node.properties
    existing["updated_at"] = datetime.utcnow().isoformat()
    
    _nodes_store[node_id] = existing
    return existing


@router.delete("/{node_id}")
async def delete_node(node_id: str):
    """Delete a knowledge graph node and its edges."""
    if node_id not in _nodes_store:
        raise HTTPException(status_code=404, detail="Node not found")
    
    del _nodes_store[node_id]
    
    # Also remove related edges (imported inline to avoid circular import at module level)
    from app.api.edges import _edges_store as _es
    edges_to_remove = [
        eid for eid, edge in list(_es.items())
        if edge["source_node_id"] == node_id or edge["target_node_id"] == node_id
    ]
    for eid in edges_to_remove:
        del _es[eid]
    
    return {"status": "success", "message": f"Node {node_id} and {len(edges_to_remove)} associated edges deleted"}
