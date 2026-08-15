"""Simulation Service — Simulations API."""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

router = APIRouter()
_store: Dict[str, Dict[str, Any]] = {}

class SimulationRun(BaseModel):
    id: str = ""
    name: str
    simulation_type: str  # pricing|marketing|renewals|upsell|retention|discount
    parameters: Dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"
    created_at: str = ""

@router.post("", response_model=SimulationRun)
async def create_simulation(sim: SimulationRun):
    sim.id = str(uuid.uuid4())
    sim.status = "running"
    sim.created_at = datetime.utcnow().isoformat()
    _store[sim.id] = sim.model_dump()
    return sim

@router.get("/{sim_id}", response_model=SimulationRun)
async def get_simulation(sim_id: str):
    if sim_id not in _store:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return _store[sim_id]

@router.get("", response_model=List[SimulationRun])
async def list_simulations(limit: int = 20):
    items = list(_store.values())
    items.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    return items[:limit]

@router.post("/{sim_id}/execute")
async def execute_simulation(sim_id: str):
    if sim_id not in _store:
        raise HTTPException(status_code=404, detail="Simulation not found")
    sim = _store[sim_id]
    sim["status"] = "completed"
    sim["results"] = {"projected_revenue": 2500000, "confidence": 0.85, "scenarios": 5}
    return {"status": "completed", "simulation_id": sim_id}
