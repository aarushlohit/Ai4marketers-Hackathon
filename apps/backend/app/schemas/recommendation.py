from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class RecommendationBase(BaseModel):
    customer_id: UUID
    type: str
    confidence: float
    expected_revenue: float = 0.0
    status: str = "Pending"
    business_reason: Optional[str] = None

class RecommendationCreate(RecommendationBase):
    pass

class RecommendationUpdate(RecommendationBase):
    customer_id: Optional[UUID] = None
    type: Optional[str] = None
    confidence: Optional[float] = None

class RecommendationResponse(RecommendationBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
