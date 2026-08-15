"""Endpoints for Subscription and Billing management, Usage Metering, and Quotas."""

from typing import Annotated, List, Dict
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser, get_current_user, get_db
from app.models.tenant import TenantModel
from app.models.customer import CustomerModel
from app.models.workflow import WorkflowModel

router = APIRouter()

PLAN_LIMITS = {
    "free": {"customers": 100, "workflows": 5, "price": 0},
    "startup": {"customers": 1000, "workflows": 20, "price": 99},
    "enterprise": {"customers": 999999, "workflows": 999999, "price": 499}
}

class PlanUpgradeRequest(BaseModel):
    plan: str # free | startup | enterprise

@router.get("/status")
async def get_billing_status(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Retrieve the current plan, usage metrics, and limits for the tenant."""
    # 1. Fetch Tenant details
    tenant = await db.get(TenantModel, user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    current_plan = tenant.plan.lower() if tenant.plan else "free"
    limits = PLAN_LIMITS.get(current_plan, PLAN_LIMITS["free"])

    # 2. Measure actual usage
    customer_count_res = await db.execute(
        select(func.count(CustomerModel.id)).where(CustomerModel.tenant_id == user.tenant_id, CustomerModel.is_deleted == False)
    )
    customer_count = customer_count_res.scalar() or 0

    workflow_count_res = await db.execute(
        select(func.count(WorkflowModel.id)).where(WorkflowModel.tenant_id == user.tenant_id)
    )
    workflow_count = workflow_count_res.scalar() or 0

    return {
        "tenant_id": user.tenant_id,
        "organization": tenant.name,
        "plan": current_plan,
        "price_monthly": limits["price"],
        "usage": {
            "customers": {
                "used": customer_count,
                "limit": limits["customers"],
                "percentage": round((customer_count / max(limits["customers"], 1)) * 100, 1)
            },
            "workflows": {
                "used": workflow_count,
                "limit": limits["workflows"],
                "percentage": round((workflow_count / max(limits["workflows"], 1)) * 100, 1)
            }
        }
    }

@router.post("/upgrade")
async def upgrade_plan(
    payload: PlanUpgradeRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Upgrade or downgrade the organization subscription tier."""
    target_plan = payload.plan.lower()
    if target_plan not in PLAN_LIMITS:
        raise HTTPException(status_code=400, detail="Invalid plan name")

    tenant = await db.get(TenantModel, user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant.plan = target_plan
    await db.commit()
    
    return {
        "status": "success",
        "message": f"Successfully updated subscription to {target_plan.capitalize()} Plan.",
        "plan": target_plan
    }

@router.get("/invoices")
async def list_invoices(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List historical billing invoices for the organization."""
    tenant = await db.get(TenantModel, user.tenant_id)
    current_plan = tenant.plan.lower() if tenant.plan else "free"
    price = PLAN_LIMITS.get(current_plan, PLAN_LIMITS["free"])["price"]

    # Mock historical invoices
    return [
        {
            "id": "INV-2026-003",
            "date": "2026-07-01",
            "amount": price,
            "status": "paid",
            "plan": current_plan
        },
        {
            "id": "INV-2026-002",
            "date": "2026-06-01",
            "amount": price,
            "status": "paid",
            "plan": current_plan
        },
        {
            "id": "INV-2026-001",
            "date": "2026-05-01",
            "amount": price,
            "status": "paid",
            "plan": current_plan
        }
    ]

@router.get("/invoices/{invoice_id}/download", response_class=PlainTextResponse)
async def download_invoice(
    invoice_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Generate and return an exportable plain-text invoice sheet."""
    tenant = await db.get(TenantModel, user.tenant_id)
    current_plan = tenant.plan.lower() if tenant.plan else "free"
    price = PLAN_LIMITS.get(current_plan, PLAN_LIMITS["free"])["price"]

    invoice_date = "2026-07-01"
    due_date = "2026-07-15"

    invoice_text = f"""
========================================================================
                      🐦 MIRACLE BIRDS PLATFORM
                          BILLING INVOICE
========================================================================

Invoice ID:    {invoice_id}
Invoice Date:  {invoice_date}
Due Date:      {due_date}
Status:        PAID (Credit Card Visa **** 4042)

------------------------------------------------------------------------
CUSTOMER DETAILS:
Tenant Name:   {tenant.name}
Tenant ID:     {tenant.id}
Email:         {user.email}

------------------------------------------------------------------------
LINE ITEMS:
1. Miracle Birds SaaS Subscription - {current_plan.capitalize()} Plan
   Monthly charge: ${price:,.2f}
   Period: 2026-07-01 to 2026-08-01
   
------------------------------------------------------------------------
SUMMARY:
Subtotal:      ${price:,.2f}
VAT / Tax:     $0.00
------------------------------------------------------------------------
TOTAL PAID:    ${price:,.2f}

========================================================================
           Thank you for business with Miracle Birds!
========================================================================
"""
    return invoice_text

async def check_quota_limits(tenant_id: UUID, resource: str, db: AsyncSession) -> bool:
    """
    Helper utility for CRM endpoints to verify limits before insertion.
    Returns True if safe, raises HTTPException 403 if quota is exceeded.
    """
    tenant = await db.get(TenantModel, tenant_id)
    plan = tenant.plan.lower() if tenant and tenant.plan else "free"
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])

    if resource == "customers":
        cust_res = await db.execute(
            select(func.count(CustomerModel.id)).where(CustomerModel.tenant_id == tenant_id, CustomerModel.is_deleted == False)
        )
        count = cust_res.scalar() or 0
        if count >= limits["customers"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Customer limit reached ({limits['customers']} limit) for plan '{plan.upper()}'. Please upgrade."
            )
            
    elif resource == "workflows":
        flow_res = await db.execute(
            select(func.count(WorkflowModel.id)).where(WorkflowModel.tenant_id == tenant_id)
        )
        count = flow_res.scalar() or 0
        if count >= limits["workflows"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Workflow limit reached ({limits['workflows']} limit) for plan '{plan.upper()}'. Please upgrade."
            )

    return True
