"""Tenant settings and destructive data-management actions."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser, get_current_user
from app.core.database import get_db
from app.models.customer import CustomerModel
from app.models.feedback import FeedbackModel
from app.models.meeting import MeetingModel
from app.models.recommendation import RecommendationModel
from app.models.workflow import WorkflowModel
from app.api.v1.endpoints.integrations import _crm_request

router = APIRouter()


@router.delete("/reset-data")
async def reset_tenant_data(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Permanently remove the tenant's CRM data and connected providers."""
    try:
        await _crm_request("DELETE", "/connections", params={"tenant_id": str(user.tenant_id)})
        for model in (FeedbackModel, MeetingModel, RecommendationModel, WorkflowModel, CustomerModel):
            await db.execute(delete(model).where(model.tenant_id == user.tenant_id))
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Could not reset tenant data")
    return {"status": "reset", "message": "CRM data and connected providers were removed."}
