"""Workflow Engine — workflow execution tracking and triggering."""

import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Dict, Any

from app.core.database import get_db
from app.models.workflow import WorkflowModel
from app.core.rule_evaluator import evaluate_condition
from app.core.celery_app import celery_app

router = APIRouter()


class TriggerRequest(BaseModel):
    event_type: str           # e.g. "churn_risk_high"
    entity_id: UUID           # customer_id or other entity
    tenant_id: UUID
    payload: Dict[str, Any] = {}


@router.post("/trigger")
async def trigger_event(payload: TriggerRequest, db: AsyncSession = Depends(get_db)):
    """
    Accept an event and find matching workflows to execute.
    Called by the ML Engine or Backend when a prediction threshold is crossed.
    """
    # Fetch active workflows for the tenant
    result = await db.execute(
        select(WorkflowModel).where(
            WorkflowModel.tenant_id == payload.tenant_id,
            WorkflowModel.is_active == True
        )
    )
    workflows = result.scalars().all()

    triggered_count = 0
    for workflow in workflows:
        # Check if condition evaluates to true
        conditions = workflow.conditions
        if evaluate_condition(conditions, payload.payload):
            # Enqueue Celery task for execution
            celery_app.send_task(
                "app.executors.tasks.run_workflow_execution",
                args=[
                    workflow.name,
                    json.dumps(workflow.actions),
                    json.dumps({
                        "customer_id": str(payload.entity_id),
                        "tenant_id": str(payload.tenant_id),
                        **payload.payload
                    })
                ]
            )
            triggered_count += 1

    return {
        "event_type": payload.event_type,
        "entity_id": str(payload.entity_id),
        "workflows_triggered": triggered_count,
        "message": f"Event received — {triggered_count} workflows queued",
    }
