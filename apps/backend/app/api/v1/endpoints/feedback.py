"""Feedback endpoints for Adaptive Learning."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.dependencies import CurrentUser, get_current_user, get_db
from app.models.feedback import FeedbackModel
from app.models.recommendation import RecommendationModel
from app.schemas.feedback import FeedbackResponse, FeedbackCreate

router = APIRouter()


@router.post("", status_code=201, response_model=FeedbackResponse)
async def submit_feedback(
    payload: FeedbackCreate,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback for an AI recommendation."""
    # Verify recommendation exists and belongs to the tenant
    result = await db.execute(
        select(RecommendationModel).where(
            RecommendationModel.id == payload.recommendation_id,
            RecommendationModel.tenant_id == user.tenant_id
        )
    )
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )

    # Save feedback
    feedback = FeedbackModel(
        tenant_id=user.tenant_id,
        recommendation_id=payload.recommendation_id,
        user_id=user.id,
        feedback_text=payload.feedback_text,
        rating=payload.rating,
        outcome_achieved=payload.outcome_achieved
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    
    # In production, we would trigger Celery or ML worker to adjust model weights
    return feedback
