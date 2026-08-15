from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    conditions: Dict[str, Any] = {}
    actions: List[Dict[str, Any]] = []
    is_active: bool = True

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowUpdate(WorkflowBase):
    name: Optional[str] = None

class WorkflowResponse(WorkflowBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
