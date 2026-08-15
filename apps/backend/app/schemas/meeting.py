from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Any

class MeetingSummaryBase(BaseModel):
    customer_id: UUID
    transcript_summary: Optional[str] = None
    action_items: List[Any] = []
    sentiment: Optional[str] = None

class MeetingSummaryCreate(MeetingSummaryBase):
    pass

class MeetingSummaryResponse(MeetingSummaryBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
