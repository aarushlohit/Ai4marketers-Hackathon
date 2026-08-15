"""Meeting Intelligence endpoints — AI-powered transcript analysis."""

from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.dependencies import CurrentUser, get_current_user, get_db
from app.models.meeting import MeetingSummaryModel
from app.models.customer import CustomerModel
from app.schemas.meeting import MeetingSummaryResponse, MeetingSummaryCreate
from app.core.ai_engine import analyze_meeting_transcript

router = APIRouter()


class MeetingAnalyzeRequest(MeetingSummaryCreate):
    title: str = "Client Call"
    date: str = "Today"
    participants: str = "Account Executive, Customer"
    duration_minutes: int = 30
    transcript: str


@router.post("/analyze", status_code=201, response_model=MeetingSummaryResponse)
async def analyze_meeting(
    payload: MeetingAnalyzeRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze a meeting transcript using the AI engine.
    Extracts: summary, sentiment, action items, churn signal, upsell opportunity.
    """
    # 1. Verify customer exists
    result = await db.execute(
        select(CustomerModel).where(
            CustomerModel.id == payload.customer_id,
            CustomerModel.tenant_id == user.tenant_id,
        )
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # 2. Call centralized AI engine for analysis
    ai_data = await analyze_meeting_transcript(
        transcript=payload.transcript,
        customer_name=f"{customer.first_name} {customer.last_name}",
        company=customer.company or "Unknown Company",
        meeting_title=payload.title,
    )

    # 3. Save to DB
    summary = MeetingSummaryModel(
        tenant_id=user.tenant_id,
        customer_id=payload.customer_id,
        transcript_summary=ai_data["summary"],
        action_items=ai_data["action_items"],
        sentiment=ai_data["sentiment"],
    )
    db.add(summary)

    # 4. Update customer churn signal if high
    if ai_data.get("churn_signal") == "high":
        customer.churn_probability = min(1.0, (customer.churn_probability or 0.0) + 0.15)
    elif ai_data.get("churn_signal") == "medium":
        customer.churn_probability = min(1.0, (customer.churn_probability or 0.0) + 0.05)

    await db.commit()
    await db.refresh(summary)

    return summary


@router.get("", response_model=List[MeetingSummaryResponse])
async def list_all_meetings(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """List all analyzed meetings for the tenant."""
    result = await db.execute(
        select(MeetingSummaryModel).where(
            MeetingSummaryModel.tenant_id == user.tenant_id,
        ).order_by(MeetingSummaryModel.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{customer_id}", response_model=List[MeetingSummaryResponse])
async def list_customer_meetings(
    customer_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """List all analyzed meetings for a specific customer."""
    result = await db.execute(
        select(MeetingSummaryModel).where(
            MeetingSummaryModel.customer_id == customer_id,
            MeetingSummaryModel.tenant_id == user.tenant_id,
        ).order_by(MeetingSummaryModel.created_at.desc())
    )
    return result.scalars().all()
