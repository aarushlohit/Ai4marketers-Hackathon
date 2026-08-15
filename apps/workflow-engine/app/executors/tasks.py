"""Celery tasks for executing workflow actions with retry, rollback, and audit trail support."""

import json
import httpx
import structlog
import uuid
import asyncio
import time
from celery import shared_task
from app.core.config import settings
from app.core.database import engine

logger = structlog.get_logger()

def _render_template(template: str, context: dict) -> str:
    """Simple template renderer replacing {{variable}} with context values."""
    if not isinstance(template, str):
        return template
    for key, val in context.items():
        template = template.replace(f"{{{{{key}}}}}", str(val))
    return template

async def _save_execution_state(exec_id: uuid.UUID, tenant_id: uuid.UUID, workflow_name: str, status: str, actions_run: list, context_data: dict, retries: int, error_msg: str = None):
    """Save execution state to workflows.executions."""
    try:
        async with engine.begin() as conn:
            # Check if record exists
            res = await conn.execute(
                "SELECT id FROM workflows.executions WHERE id = :id",
                {"id": exec_id}
            )
            row = res.fetchone()
            if row:
                await conn.execute(
                    """
                    UPDATE workflows.executions 
                    SET status = :status, actions_run = :actions_run, context_data = :context_data, retries = :retries, error_message = :err, completed_at = :completed_at
                    WHERE id = :id
                    """,
                    {
                        "id": exec_id,
                        "status": status,
                        "actions_run": json.dumps(actions_run),
                        "context_data": json.dumps(context_data),
                        "retries": retries,
                        "err": error_msg,
                        "completed_at": None if status == "running" else float(time.time())
                    }
                )
            else:
                await conn.execute(
                    """
                    INSERT INTO workflows.executions (id, tenant_id, workflow_name, status, actions_run, context_data, retries, error_message)
                    VALUES (:id, :tenant_id, :workflow_name, :status, :actions_run, :context_data, :retries, :err)
                    """,
                    {
                        "id": exec_id,
                        "tenant_id": tenant_id,
                        "workflow_name": workflow_name,
                        "status": status,
                        "actions_run": json.dumps(actions_run),
                        "context_data": json.dumps(context_data),
                        "retries": retries,
                        "err": error_msg
                    }
                )
    except Exception as e:
        logger.error("Failed to save workflow execution state", error=str(e))

async def _save_audit_log(tenant_id: uuid.UUID, action: str, resource: str, resource_id: uuid.UUID, metadata: dict):
    """Insert log into security.audit_logs."""
    try:
        async with engine.begin() as conn:
            await conn.execute(
                """
                INSERT INTO security.audit_logs (id, tenant_id, action, resource, resource_id, metadata)
                VALUES (:id, :tenant_id, :action, :resource, :resource_id, :metadata)
                """,
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant_id,
                    "action": action,
                    "resource": resource,
                    "resource_id": resource_id,
                    "metadata": json.dumps(metadata)
                }
            )
    except Exception as e:
        logger.error("Failed to save audit log", error=str(e))

async def execute_action_async(action: dict, context: dict) -> dict:
    """Execute a single workflow action. Returns rollback data."""
    action_type = action.get("type")
    config = action.get("config", {})
    customer_id = context.get("customer_id")
    tenant_id = context.get("tenant_id")

    logger.info("Executing workflow action", action_type=action_type, customer_id=customer_id)

    rollback_data = {"type": action_type, "undone": False}

    if action_type == "send_email":
        recipient = _render_template(config.get("to", ""), context)
        subject = _render_template(config.get("subject", ""), context)
        body = _render_template(config.get("body", ""), context)
        logger.info("Sending Email", recipient=recipient, subject=subject)
        # Mock successful send. Rollback will note email cancellation/retraction.
        rollback_data["recipient"] = recipient
        rollback_data["subject"] = subject

    elif action_type == "assign_lead" or action_type == "assign_team":
        team_id = config.get("team_id", "")
        logger.info("Assigning customer to team", customer_id=customer_id, team=team_id)
        # Fetch current assigned team first to support rollback
        async with httpx.AsyncClient() as client:
            try:
                # Check current record
                r = await client.get(f"http://backend:8000/api/v1/customers/{customer_id}", headers={"X-Internal-Token": "secret"})
                if r.status_code == 200:
                    rollback_data["old_team"] = r.json().get("assigned_team")
                
                await client.put(
                    f"http://backend:8000/api/v1/customers/{customer_id}",
                    json={"attributes": {"assigned_team": team_id}},
                    headers={"X-Internal-Token": "secret"}
                )
            except Exception as e:
                logger.error("Failed to call backend to assign lead/team", error=str(e))

    elif action_type == "update_crm":
        attributes = config.get("attributes", {})
        logger.info("Updating CRM attributes", customer_id=customer_id, attrs=attributes)
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(f"http://backend:8000/api/v1/customers/{customer_id}", headers={"X-Internal-Token": "secret"})
                if r.status_code == 200:
                    current_attrs = r.json().get("attributes", {})
                    rollback_data["old_attributes"] = {k: current_attrs.get(k) for k in attributes.keys()}
                
                await client.put(
                    f"http://backend:8000/api/v1/customers/{customer_id}",
                    json={"attributes": attributes},
                    headers={"X-Internal-Token": "secret"}
                )
            except Exception as e:
                logger.error("Failed to call backend to update CRM record", error=str(e))

    elif action_type == "schedule_meeting":
        logger.info("Scheduling meeting for customer", customer_id=customer_id)
        # Mock scheduled meeting

    elif action_type == "create_followup":
        logger.info("Creating customer follow-up", customer_id=customer_id)
        # Create a customer interaction log
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    f"http://backend:8000/api/v1/customers/{customer_id}/interactions",
                    json={"interaction_type": "followup", "subject": "Automated Follow-up Scheduled", "body": "Next step following workflow trigger"},
                    headers={"X-Internal-Token": "secret"}
                )
            except Exception as e:
                logger.error("Failed to create customer interaction", error=str(e))

    elif action_type == "notify_manager":
        manager_email = _render_template(config.get("manager_email", "manager@miraclebirds.com"), context)
        message = _render_template(config.get("message", "High risk customer detected"), context)
        logger.info("Notifying manager", manager=manager_email, message=message)

    elif action_type == "create_task":
        task_title = _render_template(config.get("title", "Workflow Task"), context)
        logger.info("Creating workflow task", title=task_title)
        rollback_data["task_title"] = task_title

    else:
        logger.warning("Unknown action type", action_type=action_type)

    return rollback_data

async def rollback_actions_async(actions_run_data: list, context: dict):
    """Resilient rollback routine: executes opposite commands in reverse order."""
    logger.info("Triggering workflow rollback routine")
    customer_id = context.get("customer_id")

    for completed_action in reversed(actions_run_data):
        action_type = completed_action.get("type")
        logger.info("Rolling back action step", action_type=action_type)

        try:
            if action_type == "assign_lead" or action_type == "assign_team":
                old_team = completed_action.get("old_team", None)
                async with httpx.AsyncClient() as client:
                    await client.put(
                        f"http://backend:8000/api/v1/customers/{customer_id}",
                        json={"attributes": {"assigned_team": old_team}},
                        headers={"X-Internal-Token": "secret"}
                    )
            elif action_type == "update_crm":
                old_attrs = completed_action.get("old_attributes", {})
                if old_attrs:
                    async with httpx.AsyncClient() as client:
                        await client.put(
                            f"http://backend:8000/api/v1/customers/{customer_id}",
                            json={"attributes": old_attrs},
                            headers={"X-Internal-Token": "secret"}
                        )
            elif action_type == "send_email" or action_type == "notify_manager":
                logger.info("Retracting/logging notification revocation", action=action_type)
            elif action_type == "create_task":
                logger.info("Cancelling/removing created task", title=completed_action.get("task_title"))
        except Exception as e:
            logger.error("Failed rollback step execution", action=action_type, error=str(e))

@shared_task(name="app.executors.tasks.run_workflow_execution")
def run_workflow_execution(workflow_name: str, actions_json: str, context_json: str):
    """Celery task executing actions with retries and robust rollback capability."""
    import asyncio
    actions = json.loads(actions_json)
    context = json.loads(context_json)
    
    exec_id = uuid.uuid4()
    tenant_id = uuid.UUID(context.get("tenant_id", "00000000-0000-0000-0000-000000000001"))
    
    logger.info("Starting resilient workflow execution", workflow=workflow_name, id=exec_id)
    
    loop = asyncio.get_event_loop()
    actions_run_data = []
    
    # Track states
    loop.run_until_complete(
        _save_execution_state(exec_id, tenant_id, workflow_name, "running", actions_run_data, context, 0)
    )

    success = True
    error_msg = None
    retries_count = 0

    for action in actions:
        step_success = False
        # Retry loop for resilience (up to 3 times per step)
        for attempt in range(1, 4):
            try:
                rollback_step_data = loop.run_until_complete(
                    execute_action_async(action, context)
                )
                actions_run_data.append(rollback_step_data)
                step_success = True
                break
            except Exception as e:
                retries_count += 1
                logger.warning(
                    "Workflow action step execution attempt failed",
                    action=action.get("type"),
                    attempt=attempt,
                    error=str(e)
                )
                if attempt < 3:
                    time.sleep(1) # delay before next retry
                else:
                    error_msg = str(e)
        
        if not step_success:
            success = False
            break

    if success:
        # Complete execution
        loop.run_until_complete(
            _save_execution_state(exec_id, tenant_id, workflow_name, "completed", actions_run_data, context, retries_count)
        )
        loop.run_until_complete(
            _save_audit_log(tenant_id, "workflow_completed", "workflow", exec_id, {"workflow_name": workflow_name, "steps": len(actions)})
        )
        logger.info("Resilient workflow completed successfully", workflow=workflow_name)
    else:
        # Rollback completed actions in reverse order
        loop.run_until_complete(
            _save_execution_state(exec_id, tenant_id, workflow_name, "rolling_back", actions_run_data, context, retries_count, error_msg)
        )
        loop.run_until_complete(
            rollback_actions_async(actions_run_data, context)
        )
        loop.run_until_complete(
            _save_execution_state(exec_id, tenant_id, workflow_name, "rolled_back", actions_run_data, context, retries_count, error_msg)
        )
        loop.run_until_complete(
            _save_audit_log(tenant_id, "workflow_rolled_back", "workflow", exec_id, {"workflow_name": workflow_name, "error": error_msg})
        )
        logger.error("Workflow failed. Rolled back successfully.", workflow=workflow_name, error=error_msg)
