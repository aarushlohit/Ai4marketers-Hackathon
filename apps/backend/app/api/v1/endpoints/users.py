"""User management endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser, get_current_user
from app.core.database import get_db
from app.models.user import UserModel

router = APIRouter()


class UserProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None


@router.get("/me")
async def get_me(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return the authenticated user's profile."""
    db_user = await db.get(UserModel, user.user_id)
    if not db_user:
        return {"user_id": str(user.user_id), "tenant_id": str(user.tenant_id)}
    return {
        "id": str(db_user.id),
        "email": db_user.email,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "role": db_user.role,
        "tenant_id": str(db_user.tenant_id),
        "is_active": db_user.is_active,
        "mfa_enabled": db_user.mfa_enabled,
    }


@router.put("/me")
async def update_me(
    payload: UserProfileUpdate,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update the authenticated user's profile."""
    db_user = await db.get(UserModel, user.user_id)
    if db_user:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(db_user, field, value)
        await db.commit()
        await db.refresh(db_user)
    return {"message": "Profile updated"}


@router.delete("/me/data")
async def reset_tenant_data(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete all workspace data (customers, recommendations, workflows, meetings, feedback) for the tenant."""
    from sqlalchemy import text
    tid = str(user.tenant_id)
    
    # Delete in order to respect any potential foreign keys
    await db.execute(text("DELETE FROM ai.recommendations WHERE tenant_id = :tid"), {"tid": tid})
    await db.execute(text("DELETE FROM ai.feedback_logs WHERE tenant_id = :tid"), {"tid": tid})
    await db.execute(text("DELETE FROM ai.meeting_summaries WHERE tenant_id = :tid"), {"tid": tid})
    await db.execute(text("DELETE FROM workflows.workflows WHERE tenant_id = :tid"), {"tid": tid})
    await db.execute(text("DELETE FROM customers.customers WHERE tenant_id = :tid"), {"tid": tid})
    
    await db.commit()
    return {"message": "Workspace data has been successfully reset."}
