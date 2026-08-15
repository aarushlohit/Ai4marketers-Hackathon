"""Knowledge Service — Relationship Discovery API.

Discovers relationships and patterns in the knowledge graph.
Supports: pattern matching, relationship suggestion, anomaly detection.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from collections import Counter, deque

from app.api.nodes import _nodes_store
from app.api.edges import _edges_store

router = APIRouter()


class DiscoveryResult(BaseModel):
    relationship_type: str
    source_node: Dict[str, Any]
    target_node: Dict[str, Any]
    strength: float
    supporting_evidence: List[str] = Field(default_factory=list)


class PatternMatch(BaseModel):
    pattern: str
    matches: List[Dict[str, Any]]
    count: int


VALID_PATTERN_TYPES = ["common_connections", "influential_nodes", "clusters"]


@router.post("/relationships/{node_id}")
async def discover_relationships(node_id: str, max_depth: int = 2):
    """Discover relationships for a given node up to specified depth."""
    if node_id not in _nodes_store:
        raise HTTPException(status_code=404, detail="Node not found")
    
    node = _nodes_store[node_id]
    relationships = []
    visited = set()
    
    # BFS to discover relationships using deque for O(1) operations
    queue = deque([(node_id, 0)])
    visited.add(node_id)
    
    while queue:
        current_id, depth = queue.popleft()
        if depth >= max_depth:
            continue
        
        # Find edges connected to this node
        for eid, edge in _edges_store.items():
            neighbor_id = None
            if edge["source_node_id"] == current_id:
                neighbor_id = edge["target_node_id"]
            elif edge["target_node_id"] == current_id:
                neighbor_id = edge["source_node_id"]
            
            if neighbor_id and neighbor_id not in visited and neighbor_id in _nodes_store:
                visited.add(neighbor_id)
                neighbor = _nodes_store[neighbor_id]
                
                strength = edge.get("weight", 1.0)
                if depth > 0:
                    strength *= (1.0 / (depth + 1))
                
                relationships.append(DiscoveryResult(
                    relationship_type=edge["edge_type"],
                    source_node=_nodes_store[current_id],
                    target_node=neighbor,
                    strength=round(strength, 3),
                    supporting_evidence=[
                        f"Direct {edge['edge_type']} connection",
                        f"Depth: {depth + 1}",
                        f"Edge weight: {edge.get('weight', 1.0)}",
                    ],
                ))
                
                queue.append((neighbor_id, depth + 1))
    
    relationships.sort(key=lambda r: r.strength, reverse=True)
    return {
        "source_node": node,
        "discovered_relationships": relationships[:50],
        "total_discovered": len(relationships),
    }


@router.post("/patterns/{pattern_type}")
async def discover_patterns(pattern_type: str):
    """Discover common patterns in the graph."""
    if pattern_type not in VALID_PATTERN_TYPES:
        raise HTTPException(status_code=400, detail=f"Unknown pattern type: {pattern_type}. Valid types: {', '.join(VALID_PATTERN_TYPES)}")
    
    patterns = []
    
    if pattern_type == "common_connections":
        # Find nodes that share common neighbors (e.g., two Customers connected to same Deal)
        adjacency = {}
        for eid, edge in _edges_store.items():
            src = edge["source_node_id"]
            tgt = edge["target_node_id"]
            if src not in adjacency:
                adjacency[src] = set()
            if tgt not in adjacency:
                adjacency[tgt] = set()
            adjacency[src].add(tgt)
            adjacency[tgt].add(src)
        
        # Count pairs of nodes that share neighbors
        shared_neighbor_counts = Counter()
        node_list = list(adjacency.keys())
        for i in range(len(node_list)):
            for j in range(i + 1, len(node_list)):
                common = adjacency[node_list[i]] & adjacency[node_list[j]]
                if common:
                    shared_neighbor_counts[(node_list[i], node_list[j])] = len(common)
        
        for (n1, n2), count in shared_neighbor_counts.most_common(20):
            if n1 in _nodes_store and n2 in _nodes_store:
                patterns.append(PatternMatch(
                    pattern="common_connections",
                    matches=[{
                        "node_a": _nodes_store[n1],
                        "node_b": _nodes_store[n2],
                        "shared_neighbors": count,
                    }],
                    count=count,
                ))
    
    elif pattern_type == "influential_nodes":
        # Find nodes with most connections
        degree = Counter()
        for eid, edge in _edges_store.items():
            degree[edge["source_node_id"]] += 1
            degree[edge["target_node_id"]] += 1
        
        for nid, count in degree.most_common(20):
            if nid in _nodes_store:
                patterns.append(PatternMatch(
                    pattern="influential_node",
                    matches=[{"node": _nodes_store[nid], "connection_count": count}],
                    count=count,
                ))
    
    elif pattern_type == "clusters":
        # Simple cluster detection (shared edge types)
        edge_type_counts = Counter()
        for eid, edge in _edges_store.items():
            edge_type_counts[edge["edge_type"]] += 1
        
        for edge_type, count in edge_type_counts.most_common(10):
            patterns.append(PatternMatch(
                pattern=f"{edge_type}_cluster",
                matches=[{"edge_type": edge_type, "count": count}],
                count=count,
            ))
    
    return {
        "pattern_type": pattern_type,
        "patterns": patterns,
        "total_patterns": len(patterns),
    }


@router.post("/suggest/{node_id}")
async def suggest_relationships(node_id: str):
    """Suggest potential new relationships for a node based on existing patterns."""
    if node_id not in _nodes_store:
        raise HTTPException(status_code=404, detail="Node not found")
    
    node = _nodes_store[node_id]
    existing_connections = set()
    
    # Get existing connections
    for eid, edge in _edges_store.items():
        if edge["source_node_id"] == node_id:
            existing_connections.add(edge["target_node_id"])
        if edge["target_node_id"] == node_id:
            existing_connections.add(edge["source_node_id"])
    
    # Suggest connections to nodes of related types that aren't already connected
    suggestions = []
    node_type = node["node_type"]
    
    # Define common relationship patterns
    type_connections = {
        "Customer": ["Organization", "Deal", "Meeting", "Activity", "Email", "Recommendation"],
        "Organization": ["Customer", "Deal", "Employee"],
        "Deal": ["Customer", "Meeting", "Recommendation"],
        "Meeting": ["Customer", "Deal", "Employee", "Activity"],
        "Employee": ["Organization", "Meeting"],
        "Activity": ["Customer", "Meeting", "Email"],
        "Email": ["Customer", "Activity"],
        "Recommendation": ["Customer", "Deal"],
    }
    
    target_types = type_connections.get(node_type, [])
    
    for nid, potential in _nodes_store.items():
        if nid == node_id or nid in existing_connections:
            continue
        if potential["node_type"] in target_types:
            # Calculate similarity score
            common_labels = set(node.get("labels", [])) & set(potential.get("labels", []))
            score = len(common_labels) * 0.2 + 0.5  # Base score
            
            suggestions.append({
                "suggested_node": potential,
                "relationship_type": f"HAS_{potential['node_type'].upper()}",
                "confidence": round(min(1.0, score), 2),
                "reason": f"Node type '{potential['node_type']}' commonly connects to '{node_type}'",
            })
    
    suggestions.sort(key=lambda s: s["confidence"], reverse=True)
    return {
        "source_node": node,
        "suggestions": suggestions[:20],
        "total_suggestions": len(suggestions),
    }
