"""Simulation Service — Scenarios API."""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

router = APIRouter()
_store: Dict[str, Dict[str, Any]] = {}

class Scenario(BaseModel):
    id: str = ""
    simulation_type: str
    name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    projected_revenue: Optional[float] = None
    projected_profit: Optional[float] = None
    projected_retention: Optional[float] = None
    expected_churn: Optional[float] = None
    confidence: float = 0.0
    created_at: str = ""

@router.post("", response_model=Scenario)
async def create_scenario(scenario: Scenario):
    scenario.id = str(uuid.uuid4())
    scenario.created_at = datetime.utcnow().isoformat()
    _store[scenario.id] = scenario.model_dump()
    return scenario

@router.get("/{scenario_id}", response_model=Scenario)
async def get_scenario(scenario_id: str):
    if scenario_id not in _store:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return _store[scenario_id]

@router.get("", response_model=List[Scenario])
async def list_scenarios(simulation_type: Optional[str] = None, limit: int = 20):
    items = list(_store.values())
    if simulation_type:
        items = [s for s in items if s.get("simulation_type") == simulation_type]
    items.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    return items[:limit]
