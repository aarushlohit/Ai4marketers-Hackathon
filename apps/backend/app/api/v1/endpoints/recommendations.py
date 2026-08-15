"""Recommendations endpoints."""

from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.dependencies import CurrentUser, get_current_user, get_db
from app.models.recommendation import RecommendationModel
from app.models.customer import CustomerModel
from app.schemas.recommendation import RecommendationResponse, RecommendationCreate
from app.core.config import settings

router = APIRouter()


@router.get("", response_model=List[RecommendationResponse])
async def list_recommendations(
    customer_id: UUID | None = None,
    user: Annotated[CurrentUser, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db)
):
    """List recommendations, optionally filtered by customer."""
    query = select(RecommendationModel).where(RecommendationModel.tenant_id == user.tenant_id)
    if customer_id:
        query = query.where(RecommendationModel.customer_id == customer_id)
    
    result = await db.execute(query)
    recommendations = result.scalars().all()
    return recommendations


@router.post("/generate", response_model=RecommendationResponse)
async def generate_recommendation(
    customer_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Generate recommendations for a customer using the AI Engine."""
    # 1. Fetch customer details
    result = await db.execute(
        select(CustomerModel).where(
            CustomerModel.id == customer_id,
            CustomerModel.tenant_id == user.tenant_id
        )
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # 2. Build AI payload
    churn_prob = customer.churn_probability or 0.0
    health = customer.health_score or 100.0
    lead = customer.lead_score or 0
    churn_risk_level = "high" if churn_prob > 0.5 else "medium" if churn_prob > 0.3 else "low"

    ai_payload = {
        "customer_name": f"{customer.first_name} {customer.last_name}",
        "company": customer.company,
        "churn_risk_level": churn_risk_level,
        "churn_probability": churn_prob,
        "health_score": health,
        "lead_score": lead,
        "days_since_last_interaction": 5,
        "interaction_trend": "stable",
        "interaction_summary": "Customer has active subscription and recently logged in."
    }

    ai_data = None
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                f"{settings.AI_ENGINE_URL}/recommendations/generate",
                json=ai_payload,
                timeout=15.0
            )
            r.raise_for_status()
            ai_data = r.json()
        except Exception:
            # AI Engine is unavailable — generate a deterministic local fallback
            ai_data = None

    # Local fallback recommendation when AI engine is down
    if ai_data is None:
        name = f"{customer.first_name} {customer.last_name}"
        company = customer.company or "their organization"
        if churn_prob >= 0.7:
            rec_type = "urgent_retention"
            confidence = min(0.92, churn_prob + 0.15)
            revenue = round(health * 800)
            reason = (
                f"{name} at {company} has a critical churn probability of "
                f"{round(churn_prob * 100)}%. Immediate intervention is required. "
                f"Health score of {round(health)} signals significant engagement drop."
            )
            action_plan = (
                "1. Schedule an urgent executive check-in call within 48 hours. "
                "2. Offer a personalized retention incentive (e.g., discount or feature unlock). "
                "3. Assign a dedicated Customer Success Manager for the next 30 days."
            )
        elif churn_prob >= 0.4:
            rec_type = "proactive_engagement"
            confidence = 0.78
            revenue = round(health * 1200)
            reason = (
                f"{name} at {company} shows moderate churn risk ({round(churn_prob * 100)}%). "
                f"Health score of {round(health)} suggests mild disengagement. "
                "Proactive outreach can prevent escalation."
            )
            action_plan = (
                "1. Send a personalized check-in email within 72 hours. "
                "2. Share relevant product updates and success stories. "
                "3. Offer a quarterly business review session."
            )
        elif lead >= 70:
            rec_type = "upsell_opportunity"
            confidence = 0.81
            revenue = round(lead * 500)
            reason = (
                f"{name} at {company} has a high lead score of {lead} and healthy engagement. "
                "This customer is primed for an upsell conversation."
            )
            action_plan = (
                "1. Reach out with a tailored upsell proposal for the next plan tier. "
                "2. Highlight features the customer hasn't yet adopted. "
                "3. Schedule a product demo of advanced capabilities."
            )
        else:
            rec_type = "nurture_campaign"
            confidence = 0.72
            revenue = round(health * 600)
            reason = (
                f"{name} at {company} is stable with a health score of {round(health)}. "
                "Regular nurturing will maintain satisfaction and identify growth opportunities."
            )
            action_plan = (
                "1. Enroll in the automated nurture email sequence. "
                "2. Invite to the next product webinar or community event. "
                "3. Request an NPS survey to gauge satisfaction."
            )
        ai_data = {
            "type": rec_type,
            "confidence": confidence,
            "expected_revenue": revenue,
            "business_reason": reason,
            "action_plan": action_plan,
        }

    # 3. Create database entry
    rec = RecommendationModel(
        tenant_id=user.tenant_id,
        customer_id=customer_id,
        type=ai_data["type"],
        confidence=ai_data["confidence"],
        expected_revenue=ai_data["expected_revenue"],
        status="Pending",
        business_reason=f"{ai_data['business_reason']}\nAction Plan: {ai_data['action_plan']}"
    )
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return rec


@router.post("/{recommendation_id}/accept", response_model=RecommendationResponse)
async def accept_recommendation(
    recommendation_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Accept a recommendation."""
    result = await db.execute(
        select(RecommendationModel).where(
            RecommendationModel.id == recommendation_id,
            RecommendationModel.tenant_id == user.tenant_id
        )
    )
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.status = "Accepted"
    
    # Log RL Episode State -> Action -> Reward
    try:
        import json
        cust = await db.get(CustomerModel, rec.customer_id)
        state_dict = {
            "health_score": cust.health_score or 100.0,
            "churn_probability": cust.churn_probability or 0.0,
            "lead_score": cust.lead_score or 0
        }
        await db.execute(
            """
            INSERT INTO ai.rl_episodes (tenant_id, state, action, reward, outcome, policy_version)
            VALUES (:tenant_id, :state, :action, :reward, :outcome, :policy_version)
            """,
            {
                "tenant_id": user.tenant_id,
                "state": json.dumps(state_dict),
                "action": rec.type,
                "reward": 1.0,
                "outcome": "Accepted",
                "policy_version": "v1"
            }
        )
    except Exception as e:
        print("Failed to write RL episode on accept:", e)

    await db.commit()
    await db.refresh(rec)
    return rec


@router.post("/{recommendation_id}/reject", response_model=RecommendationResponse)
async def reject_recommendation(
    recommendation_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Reject a recommendation."""
    result = await db.execute(
        select(RecommendationModel).where(
            RecommendationModel.id == recommendation_id,
            RecommendationModel.tenant_id == user.tenant_id
        )
    )
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.status = "Rejected"

    # Log RL Episode State -> Action -> Reward
    try:
        import json
        cust = await db.get(CustomerModel, rec.customer_id)
        state_dict = {
            "health_score": cust.health_score or 100.0,
            "churn_probability": cust.churn_probability or 0.0,
            "lead_score": cust.lead_score or 0
        }
        await db.execute(
            """
            INSERT INTO ai.rl_episodes (tenant_id, state, action, reward, outcome, policy_version)
            VALUES (:tenant_id, :state, :action, :reward, :outcome, :policy_version)
            """,
            {
                "tenant_id": user.tenant_id,
                "state": json.dumps(state_dict),
                "action": rec.type,
                "reward": -1.0,
                "outcome": "Rejected",
                "policy_version": "v1"
            }
        )
    except Exception as e:
        print("Failed to write RL episode on reject:", e)

    await db.commit()
    await db.refresh(rec)
    return rec

