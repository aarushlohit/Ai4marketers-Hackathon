"""Executive Intelligence endpoints — DB-backed with free AI model and CRM guardrails."""

from typing import Annotated

import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser, get_current_user, get_db
from app.models.customer import CustomerModel
from app.models.recommendation import RecommendationModel
from app.core.ai_engine import (
    build_crm_context,
    format_crm_context_as_text,
    call_llm,
    crm_chat,
    FREE_MODEL,
    CRM_SYSTEM_GUARD,
)

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=500)


@router.get("/briefing")
async def get_executive_briefing(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """Generate an AI-powered executive briefing using real DB metrics."""
    ctx = await build_crm_context(user.tenant_id, db)
    context_text = format_crm_context_as_text(ctx)

    system_prompt = (
        "You are an executive business intelligence assistant for a CRM platform. "
        "Write a concise, professional 3-paragraph executive briefing based on the live CRM metrics. "
        "Paragraph 1: current state of the customer base. "
        "Paragraph 2: risks and opportunities. "
        "Paragraph 3: three specific recommended actions. "
        "Use actual numbers and customer names where available."
    )

    at_risk_names = ", ".join(
        f"{c['name']} ({c['churn_probability']*100:.0f}%)"
        for c in ctx["at_risk_customers"][:3]
    )

    def fallback(msg: str) -> str:
        health_label = "healthy" if ctx["avg_health"] > 70 else "declining" if ctx["avg_health"] < 50 else "stable"
        risk_label = "elevated" if ctx["avg_churn"] > 0.3 else "moderate" if ctx["avg_churn"] > 0.15 else "low"
        return (
            f"**Executive Briefing — Miracle Birds CRM Intelligence**\n\n"
            f"Your portfolio of {ctx['total_customers']} customers ({ctx['active_customers']} active) "
            f"shows {health_label} engagement with an average health score of {ctx['avg_health']}/100. "
            f"Churn risk is {risk_label} at {ctx['avg_churn']*100:.1f}% across your base.\n\n"
            f"**Risks:** {ctx['at_risk_count']} accounts need immediate intervention, including "
            f"{at_risk_names or 'key accounts'}. "
            f"**Opportunities:** {ctx['hot_leads']} hot leads are primed for upsell. "
            f"Accepted AI recommendations have unlocked ${ctx['accepted_revenue']:,.0f} in pipeline.\n\n"
            f"**Recommended Actions:** "
            f"(1) Assign CSMs to the {ctx['at_risk_count']} at-risk accounts this week. "
            f"(2) Schedule upsell calls with the {ctx['hot_leads']} hot leads before quarter end. "
            f"(3) Action all {ctx['pending_recommendations']} pending AI recommendations in the platform."
        )

    briefing = await call_llm(
        system_prompt=system_prompt,
        user_message=context_text,
        fallback_fn=fallback,
        max_tokens=700,
        temperature=0.5,
    )

    return {
        "briefing": briefing,
        "metrics": {
            "total_customers": ctx["total_customers"],
            "active_customers": ctx["active_customers"],
            "average_health": ctx["avg_health"],
            "average_churn": ctx["avg_churn"],
            "at_risk_customers": ctx["at_risk_count"],
            "hot_leads": ctx["hot_leads"],
            "revenue_forecast": ctx["revenue_forecast"],
            "realized_revenue": ctx["accepted_revenue"],
        },
    }


@router.post("/ask")
async def ask_executive_question(
    payload: QuestionRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """Answer high-level business queries using live CRM data + AI (with guardrails)."""
    response = await crm_chat(
        user_message=payload.question,
        tenant_id=user.tenant_id,
        db=db,
    )
    return {"answer": response, "model": FREE_MODEL}
