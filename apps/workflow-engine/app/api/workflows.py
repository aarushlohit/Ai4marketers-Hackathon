"""Workflow Engine — workflow definition CRUD."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from uuid import UUID
from typing import Optional, List, Dict, Any

from app.core.database import get_db
from app.models.workflow import WorkflowModel

router = APIRouter()


class WorkflowDefinitionBase(BaseModel):
    name: str
    description: Optional[str] = None
    conditions: Dict[str, Any] = {}
    actions: List[Dict[str, Any]] = []
    is_active: bool = True


class WorkflowDefinitionCreate(WorkflowDefinitionBase):
    tenant_id: UUID


class WorkflowDefinitionResponse(WorkflowDefinitionBase):
    id: UUID
    tenant_id: UUID

    model_config = ConfigDict(from_attributes=True)


@router.get("", response_model=List[WorkflowDefinitionResponse])
async def list_workflows(tenant_id: UUID, db: AsyncSession = Depends(get_db)):
    """List all workflow definitions for a tenant."""
    result = await db.execute(
        select(WorkflowModel).where(WorkflowModel.tenant_id == tenant_id)
    )
    workflows = result.scalars().all()
    return workflows


@router.post("", status_code=201, response_model=WorkflowDefinitionResponse)
async def create_workflow(payload: WorkflowDefinitionCreate, db: AsyncSession = Depends(get_db)):
    """Create a new workflow automation rule."""
    workflow = WorkflowModel(
        tenant_id=payload.tenant_id,
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


@router.put("/{workflow_id}/toggle", response_model=WorkflowDefinitionResponse)
async def toggle_workflow(workflow_id: UUID, db: AsyncSession = Depends(get_db)):
    """Enable or disable a workflow."""
    result = await db.execute(
        select(WorkflowModel).where(WorkflowModel.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow.is_active = not workflow.is_active
    await db.commit()
    await db.refresh(workflow)
    return workflow


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a workflow definition."""
    result = await db.execute(
        select(WorkflowModel).where(WorkflowModel.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    await db.execute(delete(WorkflowModel).where(WorkflowModel.id == workflow_id))
    await db.commit()
    return None
