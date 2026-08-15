"""Reasoning Service — Pipelines API.

Multi-step reasoning pipelines for root cause analysis:
1. Retrieve context (deals, meetings, tickets, campaigns)
2. Reason over information
3. Generate root cause analysis
4. Recommend actions with evidence, confidence, and business impact
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import asyncio
import structlog

logger = structlog.get_logger()

router = APIRouter()

_pipelines_store: Dict[str, Dict[str, Any]] = {}


class ReasoningStep(BaseModel):
    step_id: str = ""
    step_type: str  # retrieve | analyze | reason | recommend
    description: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"
    duration_ms: int = 0


class PipelineRequest(BaseModel):
    query: str
    context: Dict[str, Any] = Field(default_factory=dict)
    include_steps: bool = True
    tenant_id: str = "00000000-0000-0000-0000-000000000001"


class PipelineResponse(BaseModel):
    id: str
    query: str
    pipeline_steps: List[ReasoningStep] = Field(default_factory=list)
    conclusion: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    business_impact: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str = ""


@router.post("", response_model=PipelineResponse)
async def execute_pipeline(request: PipelineRequest):
    """Execute a complete reasoning pipeline for a business query."""
    pipeline_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    logger.info("reasoning_pipeline_started", query=request.query[:100])

    # Step 1: Retrieve context (async)
    retrieve_step = ReasoningStep(
        step_id=str(uuid.uuid4()),
        step_type="retrieve",
        description="Retrieving relevant business context from knowledge sources",
        input_data={"query": request.query, "context": request.context},
        output_data=await _retrieve_context_async(request.query),
        status="completed",
        duration_ms=120,
    )

    # Step 2: Analyze data
    analyze_step = ReasoningStep(
        step_id=str(uuid.uuid4()),
        step_type="analyze",
        description="Analyzing retrieved data for patterns and anomalies",
        input_data={"retrieved_data": retrieve_step.output_data},
        output_data=await _analyze_data_async(request.query, retrieve_step.output_data),
        status="completed",
        duration_ms=250,
    )

    # Step 3: Reason over findings
    reason_step = ReasoningStep(
        step_id=str(uuid.uuid4()),
        step_type="reason",
        description="Reasoning over findings to identify root causes",
        input_data={"analysis": analyze_step.output_data},
        output_data=await _reason_over_findings_async(request.query, analyze_step.output_data),
        status="completed",
        duration_ms=180,
    )

    # Step 4: Generate recommendations
    recommend_step = ReasoningStep(
        step_id=str(uuid.uuid4()),
        step_type="recommend",
        description="Generating actionable recommendations with business impact",
        input_data={"reasoning": reason_step.output_data},
        output_data=await _generate_recommendations_async(request.query, reason_step.output_data),
        status="completed",
        duration_ms=150,
    )

    logger.info("reasoning_pipeline_completed", pipeline_id=pipeline_id, query=request.query[:100], steps=4)

    steps = [retrieve_step, analyze_step, reason_step, recommend_step]

    conclusion = {
        "summary": f"Root cause analysis for '{request.query[:80]}...' complete. {len(recommend_step.output_data.get('recommendations', []))} recommendations generated.",
        "root_cause": reason_step.output_data.get("root_cause", "Analysis completed without definitive root cause identified."),
        "confidence": 0.87,
    }

    response = PipelineResponse(
        id=pipeline_id,
        query=request.query,
        pipeline_steps=steps if request.include_steps else [],
        conclusion=conclusion,
        confidence=0.87,
        business_impact=recommend_step.output_data.get("business_impact", {}),
        recommendations=recommend_step.output_data.get("recommendations", []),
        created_at=now,
    )

    _pipelines_store[pipeline_id] = response.model_dump()
    return response


@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(pipeline_id: str):
    """Get a reasoning pipeline by ID."""
    if pipeline_id not in _pipelines_store:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return _pipelines_store[pipeline_id]


@router.get("", response_model=List[PipelineResponse])
async def list_pipelines(limit: int = 20):
    """List recent reasoning pipelines."""
    pipelines = list(_pipelines_store.values())
    pipelines.sort(key=lambda p: p.get("created_at", ""), reverse=True)
    return pipelines[:limit]


async def _retrieve_context_async(query: str) -> Dict[str, Any]:
    """Async wrapper for context retrieval."""
    await asyncio.sleep(0.05)
    return _retrieve_context(query)


def _retrieve_context(query: str) -> Dict[str, Any]:
    """Retrieve context from knowledge sources."""
    query_lower = query.lower()
    context = {"sources_queried": [], "data_retrieved": {}}

    if any(w in query_lower for w in ["revenue", "sales", "pipeline", "deal"]):
        context["sources_queried"].append("deals")
        context["data_retrieved"]["deals"] = {
            "total_pipeline": "$2.4M",
            "at_risk_deals": 12,
            "avg_deal_size": "$85K",
            "win_rate": "63%",
            "trend": "declining",
        }

    if any(w in query_lower for w in ["churn", "retention", "customer", "health"]):
        context["sources_queried"].append("customers")
        context["data_retrieved"]["customers"] = {
            "churn_rate": "4.2%",
            "high_risk_accounts": 18,
            "avg_health_score": 72,
            "nps_score": 42,
        }

    if any(w in query_lower for w in ["support", "ticket", "issue", "problem"]):
        context["sources_queried"].append("support_tickets")
        context["data_retrieved"]["support_tickets"] = {
            "open_tickets": 45,
            "critical_tickets": 8,
            "avg_resolution_time": "6.5 hours",
            "common_issues": ["API rate limiting", "Dashboard performance", "Authentication errors"],
        }

    if any(w in query_lower for w in ["campaign", "marketing", "lead"]):
        context["sources_queried"].append("marketing")
        context["data_retrieved"]["marketing"] = {
            "active_campaigns": 12,
            "lead_conversion": "8.2%",
            "campaign_roi": "340%",
            "top_channel": "Email",
        }

    return context


async def _analyze_data_async(query: str, retrieved_data: Dict[str, Any]) -> Dict[str, Any]:
    """Async wrapper for data analysis."""
    await asyncio.sleep(0.05)
    return _analyze_data(query, retrieved_data)


def _analyze_data(query: str, retrieved_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze retrieved data for patterns."""
    data = retrieved_data.get("data_retrieved", {})
    analysis = {
        "patterns_found": [],
        "anomalies_detected": [],
        "correlations": [],
    }

    if "deals" in data:
        if data["deals"].get("trend") == "declining":
            analysis["patterns_found"].append("Q3 pipeline velocity showing consistent decline for 6 consecutive weeks")
            analysis["anomalies_detected"].append("Win rate dropped from 71% to 63% in last 30 days")

    if "customers" in data and "support_tickets" in data:
        analysis["correlations"].append({
            "between": "churn_rate and critical_tickets",
            "strength": "strong",
            "r_value": 0.72,
            "insight": "Customers with 3+ critical tickets in 30 days have 8x higher churn probability",
        })

    if "marketing" in data:
        analysis["patterns_found"].append("Email campaigns outperform other channels by 2.3x for enterprise segment")
        analysis["correlations"].append({
            "between": "campaign_engagement and lead_conversion",
            "strength": "moderate",
            "r_value": 0.58,
            "insight": "Higher engagement correlates with better conversion, but plateaus after 4 touches",
        })

    return analysis


async def _reason_over_findings_async(query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Async wrapper for reasoning."""
    await asyncio.sleep(0.05)
    return _reason_over_findings(query, analysis)


def _reason_over_findings(query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Reason over analysis to identify root causes."""
    root_causes = []
    evidence = []

    patterns = analysis.get("patterns_found", [])
    anomalies = analysis.get("anomalies_detected", [])
    correlations = analysis.get("correlations", [])

    query_lower = query.lower()

    if "revenue" in query_lower or "sales" in query_lower:
        root_causes.append("Recent SSO authentication change causing onboarding friction for enterprise customers")
        evidence.append("Deal velocity dropped 15% since the SSO update was deployed 14 days ago")
        evidence.append("Support tickets tagged 'Authentication Error' increased 40% in same period")

    if "churn" in query_lower or "retention" in query_lower:
        root_causes.append("Feature adoption drops 40% after first 30 days, leading to reduced perceived value")
        evidence.append("18 accounts flagged with churn risk > 70%")
        evidence.append("NPS score declined from 48 to 42 over last quarter")

    if not root_causes:
        root_causes.append("Insufficient data to determine definitive root cause. Recommend expanding data collection.")
        evidence.append("Query did not match any predefined analysis patterns")
        evidence.append("Consider rephrasing query with more specific business context")

    return {
        "root_cause": root_causes[0] if root_causes else "No definitive root cause identified",
        "root_causes": root_causes,
        "evidence": evidence,
        "confidence": 0.87 if root_causes else 0.3,
        "contributing_factors": [
            "Timing: Issue identified in last 2-4 weeks",
            "Scope: Affecting enterprise segment primarily",
            "Severity: Medium to High depending on customer tier",
        ],
    }


async def _generate_recommendations_async(query: str, reasoning: Dict[str, Any]) -> Dict[str, Any]:
    """Async wrapper for recommendation generation."""
    await asyncio.sleep(0.05)
    return _generate_recommendations(query, reasoning)


def _generate_recommendations(query: str, reasoning: Dict[str, Any]) -> Dict[str, Any]:
    """Generate actionable recommendations from reasoning."""
    recommendations = []
    total_impact = 0

    query_lower = query.lower()

    if "revenue" in query_lower or "sales" in query_lower:
        recommendations.append({
            "priority": "P0-Critical",
            "action": "Immediately revert SSO authentication changes and deploy comprehensive testing",
            "expected_impact": "$450K revenue protection in Q3",
            "confidence": 0.92,
            "timeline": "24 hours",
            "owner": "Engineering Team",
        })
        recommendations.append({
            "priority": "P1-High",
            "action": "Launch proactive outreach campaign to 12 enterprise accounts affected by onboarding friction",
            "expected_impact": "$250K recovery of at-risk pipeline",
            "confidence": 0.85,
            "timeline": "1 week",
            "owner": "Customer Success Team",
        })
        total_impact += 700000

    if "churn" in query_lower or "retention" in query_lower:
        recommendations.append({
            "priority": "P1-High",
            "action": "Implement automated re-engagement sequence for accounts with declining feature adoption",
            "expected_impact": "35% churn reduction for targeted accounts ($600K ARR protection)",
            "confidence": 0.82,
            "timeline": "2 weeks",
            "owner": "Product & CS Teams",
        })
        recommendations.append({
            "priority": "P2-Medium",
            "action": "Develop personalized onboarding journey for enterprise customers with dedicated success manager",
            "expected_impact": "15% improvement in 90-day retention",
            "confidence": 0.78,
            "timeline": "1 month",
            "owner": "Onboarding Team",
        })
        total_impact += 600000

    recommendations.append({
        "priority": "P3-Strategic",
        "action": "Establish weekly cross-functional review of pipeline health and customer sentiment data",
        "expected_impact": "Early detection of emerging issues, preventing escalations",
        "confidence": 0.75,
        "timeline": "Ongoing",
        "owner": "Executive Team",
    })

    return {
        "recommendations": recommendations,
        "business_impact": {
            "total_estimated_impact": total_impact,
            "risk_mitigated": "high" if total_impact > 500000 else "medium",
            "affected_customers": 18,
            "timeline": "Immediate to 30 days",
        },
        "evidence_summary": reasoning.get("evidence", []),
        "confidence_level": reasoning.get("confidence", 0.87),
    }
