"""Recommendation Engine — generates prescriptive next steps for customers."""

import json
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID

from app.core.llm import get_llm
from app.prompts.crm_copilot import NEXT_BEST_ACTION_PROMPT
from langchain_core.messages import HumanMessage

router = APIRouter()


class RecommendationRequest(BaseModel):
    customer_name: str
    company: Optional[str] = None
    churn_risk_level: str
    churn_probability: float
    health_score: float
    lead_score: int
    days_since_last_interaction: int
    interaction_trend: str
    interaction_summary: str


class RecommendationOutput(BaseModel):
    type: str
    confidence: float
    expected_revenue: float
    business_reason: str
    action_plan: str


@router.post("/generate", response_model=RecommendationOutput)
async def generate_recommendation(payload: RecommendationRequest):
    """Generate upsell, cross-sell, discount, or engagement recommendations."""
    prompt_text = NEXT_BEST_ACTION_PROMPT.format(
        customer_name=payload.customer_name,
        company=payload.company or "N/A",
        churn_risk_level=payload.churn_risk_level,
        churn_probability=payload.churn_probability,
        health_score=payload.health_score,
        lead_score=payload.lead_score,
        days_since_last_interaction=payload.days_since_last_interaction,
        interaction_trend=payload.interaction_trend,
        interaction_summary=payload.interaction_summary
    )

    prompt_text += """
    
    CRITICAL: You MUST classify this suggestion into one of: "Upsell", "Cross-sell", "Discount Suggestion", "Renewal Strategy", "Retention Campaign", or "Customer Engagement Strategy".
    Return ONLY a valid JSON object matching this schema:
    {
      "type": "one of the types listed above",
      "confidence": 0.0 to 1.0 representing confidence in this recommendation,
      "expected_revenue": float representing expected dollar value (0.0 if unknown),
      "business_reason": "2-3 sentences explaining why this recommendation makes sense based on the health score and interactions",
      "action_plan": "Specific action steps for the sales rep"
    }
    """

    llm = get_llm()
    try:
        response = await llm.ainvoke([HumanMessage(content=prompt_text)])
        output_text = response.content.strip()

        if output_text.startswith("```json"):
            output_text = output_text[7:]
        if output_text.endswith("```"):
            output_text = output_text[:-3]
        output_text = output_text.strip()

        parsed = json.loads(output_text)
        return RecommendationOutput(
            type=parsed.get("type", "Customer Engagement Strategy"),
            confidence=float(parsed.get("confidence", 0.7)),
            expected_revenue=float(parsed.get("expected_revenue", 0.0)),
            business_reason=parsed.get("business_reason", "No reason provided."),
            action_plan=parsed.get("action_plan", "Contact customer to review account status.")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendation: {str(e)}"
        )
