"""Knowledge Service — Graph Traversal API.

Supports: BFS, DFS, shortest path, neighborhood discovery.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from collections import deque

from app.api.nodes import _nodes_store
from app.api.edges import _edges_store

router = APIRouter()


class TraversalRequest(BaseModel):
    start_node_id: str
    max_depth: int = 3
    edge_types: Optional[List[str]] = None
    node_types: Optional[List[str]] = None


class PathResult(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    total_distance: int


@router.post("/bfs", response_model=List[Dict[str, Any]])
async def breadth_first_search(request: TraversalRequest):
    """BFS traversal from a starting node."""
    if request.start_node_id not in _nodes_store:
        raise HTTPException(status_code=404, detail="Start node not found")
    
    visited = set()
    queue = deque([(request.start_node_id, 0)])
    result = []
    
    # Build adjacency list
    adjacency = {}
    for eid, edge in _edges_store.items():
        src = edge["source_node_id"]
        tgt = edge["target_node_id"]
        
        if request.edge_types and edge["edge_type"] not in request.edge_types:
            continue
        
        if src not in adjacency:
            adjacency[src] = []
        adjacency[src].append((tgt, edge["edge_type"], eid))
        
        if tgt not in adjacency:
            adjacency[tgt] = []
        adjacency[tgt].append((src, edge["edge_type"], eid))
    
    while queue:
        node_id, depth = queue.popleft()
        
        if node_id in visited or depth > request.max_depth:
            continue
        
        visited.add(node_id)
        
        if node_id in _nodes_store:
            node = _nodes_store[node_id]
            if request.node_types and node["node_type"] not in request.node_types:
                continue
            result.append({
                "node": node,
                "depth": depth,
                "connections": adjacency.get(node_id, []),
            })
        
        for neighbor, _, _ in adjacency.get(node_id, []):
            if neighbor not in visited:
                queue.append((neighbor, depth + 1))
    
    return result


@router.post("/shortest-path", response_model=PathResult)
async def find_shortest_path(start_node_id: str, end_node_id: str):
    """Find shortest path between two nodes (BFS)."""
    if start_node_id not in _nodes_store:
        raise HTTPException(status_code=404, detail="Start node not found")
    if end_node_id not in _nodes_store:
        raise HTTPException(status_code=404, detail="End node not found")
    
    # Build adjacency
    adjacency = {}
    for eid, edge in _edges_store.items():
        src = edge["source_node_id"]
        tgt = edge["target_node_id"]
        if src not in adjacency:
            adjacency[src] = []
        adjacency[src].append((tgt, eid, edge))
        if tgt not in adjacency:
            adjacency[tgt] = []
        adjacency[tgt].append((src, eid, edge))
    
    # BFS for shortest path
    queue = deque([(start_node_id, [start_node_id], [])])
    visited = {start_node_id}
    
    while queue:
        current, path, edge_path = queue.popleft()
        
        if current == end_node_id:
            return PathResult(
                nodes=[_nodes_store[nid] for nid in path],
                edges=edge_path,
                total_distance=len(edge_path),
            )
        
        for neighbor, eid, edge in adjacency.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor], edge_path + [edge]))
    
    raise HTTPException(status_code=404, detail="No path found between nodes")


@router.post("/neighborhood", response_model=List[Dict[str, Any]])
async def get_neighborhood(node_id: str, depth: int = 2):
    """Get the neighborhood around a node (connected nodes up to depth)."""
    if node_id not in _nodes_store:
        raise HTTPException(status_code=404, detail="Node not found")
    
    visited = set()
    queue = deque([(node_id, 0)])
    neighborhood = []
    
    # Build adjacency
    adjacency = {}
    for eid, edge in _edges_store.items():
        src = edge["source_node_id"]
        tgt = edge["target_node_id"]
        if src not in adjacency:
            adjacency[src] = []
        adjacency[src].append({"node_id": tgt, "edge_type": edge["edge_type"], "edge_id": eid})
        if tgt not in adjacency:
            adjacency[tgt] = []
        adjacency[tgt].append({"node_id": src, "edge_type": edge["edge_type"], "edge_id": eid})
    
    while queue:
        current, current_depth = queue.popleft()
        
        if current in visited or current_depth > depth:
            continue
        
        visited.add(current)
        
        if current in _nodes_store and current != node_id:
            neighborhood.append({
                "node": _nodes_store[current],
                "depth": current_depth,
                "connections": [
                    c for c in adjacency.get(current, [])
                    if c["node_id"] in visited or any(
                        p[0] == c["node_id"] for p in queue
                    )
                ],
            })
        
        for neighbor in adjacency.get(current, []):
            if neighbor["node_id"] not in visited:
                queue.append((neighbor["node_id"], current_depth + 1))
    
    return neighborhood
