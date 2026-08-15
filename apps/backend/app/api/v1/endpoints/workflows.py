"""Workflow automation endpoints."""

from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.api.dependencies import CurrentUser, get_current_user, get_db
from app.models.workflow import WorkflowModel
from app.schemas.workflow import WorkflowCreate, WorkflowResponse, WorkflowUpdate

router = APIRouter()


@router.get("", response_model=List[WorkflowResponse])
async def list_workflows(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List all workflow definitions for the tenant."""
    result = await db.execute(
        select(WorkflowModel).where(WorkflowModel.tenant_id == user.tenant_id)
    )
    workflows = result.scalars().all()
    return workflows


@router.post("", status_code=201, response_model=WorkflowResponse)
async def create_workflow(
    payload: WorkflowCreate,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new workflow automation rule."""
    from app.api.v1.endpoints.billing import check_quota_limits
    await check_quota_limits(user.tenant_id, "workflows", db)

    workflow = WorkflowModel(

        tenant_id=user.tenant_id,
        name=payload.name,
        description=payload.description,
        conditions=payload.conditions,
        actions=payload.actions,
        is_active=payload.is_active,
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    return workflow


@router.put("/{workflow_id}/toggle", response_model=WorkflowResponse)
async def toggle_workflow(
    workflow_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Enable or disable a workflow."""
    result = await db.execute(
        select(WorkflowModel).where(
            WorkflowModel.id == workflow_id,
            WorkflowModel.tenant_id == user.tenant_id
        )
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow.is_active = not workflow.is_active
    await db.commit()
    await db.refresh(workflow)
    return workflow


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(
    workflow_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a workflow definition."""
    result = await db.execute(
        select(WorkflowModel).where(
            WorkflowModel.id == workflow_id,
            WorkflowModel.tenant_id == user.tenant_id
        )
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    await db.delete(workflow)
    await db.commit()
    return None
