"""Customer Digital Twin Service — Twins API.

Generates and manages AI Digital Twins for every customer.
Predicts: buying behaviour, price sensitivity, renewal probability, 
risk level, preferred channel, communication frequency, product affinity, CLV.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

router = APIRouter()

# In-memory twin store (replace with PostgreSQL pgvector in production)
_twins_store: Dict[str, Dict[str, Any]] = {}


class CustomerTwin(BaseModel):
    id: str = ""
    tenant_id: str = "00000000-0000-0000-0000-000000000001"
    customer_id: str
    customer_name: str = ""
    buying_behaviour: Dict[str, Any] = Field(default_factory=lambda: {
        "purchase_frequency": "quarterly",
        "avg_order_value": 15000,
        "preferred_products": [],
        "decision_cycle_days": 45,
    })
    price_sensitivity: float = 0.5
    renewal_probability: float = 0.85
    risk_level: str = "low"  # low | medium | high | critical
    preferred_channel: str = "email"
    communication_frequency: str = "weekly"
    product_affinity: List[Dict[str, Any]] = Field(default_factory=list)
    lifetime_value: float = 0.0
    attributes: Dict[str, Any] = Field(default_factory=dict)
    last_updated_at: str = ""
    created_at: str = ""


class TwinUpdateEvent(BaseModel):
    customer_id: str
    event_type: str  # interaction | meeting | ticket | email | deal_update
    event_data: Dict[str, Any] = Field(default_factory=dict)


@router.post("", response_model=CustomerTwin)
async def create_twin(twin: CustomerTwin):
    """Generate a new AI Digital Twin for a customer."""
    twin_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    twin.id = twin_id
    twin.created_at = now
    twin.last_updated_at = now
    
    # Auto-calculate initial predictions
    twin = _calculate_twin_predictions(twin)
    
    _twins_store[twin_id] = twin.model_dump()
    _twins_store[f"customer_{twin.customer_id}"] = twin.model_dump()
    return twin


@router.get("/{twin_id}", response_model=CustomerTwin)
async def get_twin(twin_id: str):
    """Get a digital twin by ID."""
    if twin_id in _twins_store:
        return _twins_store[twin_id]
    # Try customer_id lookup
    key = f"customer_{twin_id}"
    if key in _twins_store:
        return _twins_store[key]
    raise HTTPException(status_code=404, detail="Digital twin not found")


@router.get("/customer/{customer_id}", response_model=CustomerTwin)
async def get_twin_by_customer(customer_id: str):
    """Get a digital twin by customer ID."""
    key = f"customer_{customer_id}"
    if key not in _twins_store:
        # Auto-generate twin if not exists
        twin = CustomerTwin(customer_id=customer_id)
        return await create_twin(twin)
    return _twins_store[key]


@router.get("", response_model=List[CustomerTwin])
async def list_twins(
    risk_level: Optional[str] = None,
    min_clv: Optional[float] = None,
    limit: int = Query(default=50, le=200),
):
    """List all digital twins with optional filters."""
    twins = [t for key, t in _twins_store.items() if not key.startswith("customer_")]
    
    if risk_level:
        twins = [t for t in twins if t.get("risk_level") == risk_level]
    if min_clv is not None:
        twins = [t for t in twins if t.get("lifetime_value", 0) >= min_clv]
    
    twins.sort(key=lambda t: t.get("lifetime_value", 0), reverse=True)
    return twins[:limit]


@router.post("/{twin_id}/update", response_model=CustomerTwin)
async def update_twin_from_event(twin_id: str, event: TwinUpdateEvent):
    """Update a digital twin after a CRM event."""
    key = twin_id
    if key not in _twins_store:
        key = f"customer_{twin_id}"
    if key not in _twins_store:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    
    twin_data = _twins_store[key].copy()
    twin = CustomerTwin(**twin_data)
    
    # Update twin based on event type
    if event.event_type == "interaction":
        sentiment = event.event_data.get("sentiment", 0)
        if sentiment < -0.3:
            twin.risk_level = "high" if twin.risk_level != "critical" else twin.risk_level
        elif sentiment > 0.5:
            twin.renewal_probability = min(1.0, twin.renewal_probability + 0.05)
    
    elif event.event_type == "ticket":
        ticket_priority = event.event_data.get("priority", "low")
        if ticket_priority in ("high", "critical"):
            twin.risk_level = "high"
            twin.renewal_probability = max(0.0, twin.renewal_probability - 0.1)
    
    elif event.event_type == "deal_update":
        deal_value = event.event_data.get("value", 0)
        if deal_value > 0:
            twin.lifetime_value += deal_value
            twin.renewal_probability = min(1.0, twin.renewal_probability + 0.02)
    
    twin.last_updated_at = datetime.utcnow().isoformat()
    twin = _calculate_twin_predictions(twin)
    
    _twins_store[twin_id] = twin.model_dump()
    _twins_store[f"customer_{twin.customer_id}"] = twin.model_dump()
    return twin


@router.delete("/{twin_id}")
async def delete_twin(twin_id: str):
    """Delete a digital twin."""
    if twin_id in _twins_store:
        twin_data = _twins_store[twin_id]
        cust_key = f"customer_{twin_data.get('customer_id', '')}"
        del _twins_store[twin_id]
        if cust_key in _twins_store:
            del _twins_store[cust_key]
        return {"status": "success", "message": f"Digital twin {twin_id} deleted"}
    raise HTTPException(status_code=404, detail="Digital twin not found")


@router.post("/batch-update")
async def batch_update_twins(events: List[TwinUpdateEvent]):
    """Batch update twins from multiple CRM events."""
    results = []
    for event in events:
        try:
            twin = await update_twin_from_event(event.customer_id, event)
            results.append({"customer_id": event.customer_id, "status": "updated"})
        except HTTPException:
            results.append({"customer_id": event.customer_id, "status": "not_found"})
    return {"results": results, "total": len(results), "updated": sum(1 for r in results if r["status"] == "updated")}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _calculate_twin_predictions(twin: CustomerTwin) -> CustomerTwin:
    """Calculate AI predictions based on twin attributes."""
    # Price sensitivity: higher for customers with many tickets or churn risk
    if twin.risk_level in ("high", "critical"):
        twin.price_sensitivity = min(1.0, twin.price_sensitivity + 0.15)
    
    # Renewal probability based on risk level
    risk_renewal_map = {
        "critical": 0.15,
        "high": 0.45,
        "medium": 0.70,
        "low": 0.90,
    }
    twin.renewal_probability = risk_renewal_map.get(twin.risk_level, 0.85)
    
    # CLV estimate (simplified)
    base_clv = twin.lifetime_value or 50000
    risk_multiplier = {"critical": 0.3, "high": 0.6, "medium": 0.8, "low": 1.0}
    twin.lifetime_value = base_clv * risk_multiplier.get(twin.risk_level, 1.0)
    
    return twin
