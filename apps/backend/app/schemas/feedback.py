from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class FeedbackBase(BaseModel):
    recommendation_id: UUID
    user_id: UUID
    feedback_text: Optional[str] = None
    rating: Optional[int] = None
    outcome_achieved: bool = False

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackResponse(FeedbackBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
