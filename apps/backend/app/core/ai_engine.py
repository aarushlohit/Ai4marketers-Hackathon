"""
Centralized AI Engine for Miracle Birds CRM.

All AI-powered endpoints across the platform route through this module.
Includes:
  - LLM call via DeepSeek V4 Flash Free (opencode.ai)
  - CRM Guardrails — blocks non-business queries
  - Context builder using live DB data
  - Structured fallbacks for every intent
"""

import re
import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import CustomerModel
from app.models.recommendation import RecommendationModel

OPENCODE_API_URL = "https://opencode.ai/zen/v1/chat/completions"
FREE_MODEL = "deepseek-v4-flash-free"

# ── CRM Guardrails ─────────────────────────────────────────────────────
# Topics explicitly allowed (CRM / business domain)
ALLOWED_KEYWORDS = [
    "customer", "churn", "lead", "revenue", "forecast", "health", "score",
    "recommendation", "risk", "meeting", "transcript", "summary", "action",
    "workflow", "analytics", "pipeline", "deal", "upsell", "sales", "crm",
    "account", "contact", "retention", "engagement", "sentiment", "trend",
    "data", "report", "metric", "performance", "segment", "campaign",
    "integration", "frappe", "zoho", "salesforce", "hubspot", "prediction",
    "executive", "briefing", "at-risk", "hot lead", "subscription",
    "renewal", "onboarding", "csm", "support", "ticket", "nps", "mrr",
    "arr", "ltv", "lifetime", "value", "conversion", "opportunity",
    "who", "what", "which", "how", "when", "show", "list", "give",
    "tell", "analyze", "analyse", "explain", "describe", "find"
]

# Topics that are clearly off-topic — hard block
BLOCKED_PATTERNS = [
    r"\b(c\+\+|python|java|javascript|typescript|rust|golang|code|program)\b",
    r"\b(compiler|runtime|function|class|variable|loop|array|recursion)\b",
    r"\b(recipe|cook|food|diet|exercise|workout|movie|game|sport)\b",
    r"\b(politics|religion|war|gun|weapon|hack|exploit|malware)\b",
    r"\b(joke|poem|story|essay|fiction|homework|assignment)\b",
    r"\b(translate|language|grammar|spelling)\b",
]

CRM_SYSTEM_GUARD = """
You are the Miracle Birds AI CRM Copilot — a specialized AI assistant embedded 
inside an enterprise CRM platform.

STRICT RULES:
1. You ONLY answer questions related to: customers, churn risk, lead scoring, 
   revenue forecasts, sales pipelines, meeting analysis, CRM integrations, 
   AI recommendations, customer health scores, workflows, and general business strategy.
2. If the user asks ANYTHING outside CRM/business context (e.g., coding, recipes, 
   jokes, math problems, general knowledge), respond EXACTLY with:
   "I'm a CRM Copilot and can only help with business and customer-related questions. 
   Try asking about your customers, churn risk, leads, or revenue."
3. Always use the live CRM data provided in your context. Be specific with names and numbers.
4. Keep answers concise, actionable, and business-focused.
"""


def _is_blocked(message: str) -> bool:
    """Return True if the message is clearly off-topic/non-CRM."""
    msg_lower = message.lower()

    # Hard block check
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, msg_lower, re.IGNORECASE):
            return True

    return False


def _guardrail_response() -> str:
    return (
        "I'm a CRM Copilot and can only help with business and customer-related questions. "
        "Try asking about your customers, churn risk, leads, or revenue."
    )


async def build_crm_context(tenant_id, db: AsyncSession) -> dict:
    """Fetch real CRM metrics from DB and return a structured context dict."""
    total = await db.scalar(
        select(func.count(CustomerModel.id)).where(
            CustomerModel.tenant_id == tenant_id,
            CustomerModel.is_deleted.is_(False),
        )
    ) or 0

    active = await db.scalar(
        select(func.count(CustomerModel.id)).where(
            CustomerModel.tenant_id == tenant_id,
            CustomerModel.status == "active",
            CustomerModel.is_deleted.is_(False),
        )
    ) or 0

    at_risk_count = await db.scalar(
        select(func.count(CustomerModel.id)).where(
            CustomerModel.tenant_id == tenant_id,
            CustomerModel.churn_probability > 0.5,
            CustomerModel.is_deleted.is_(False),
        )
    ) or 0

    hot_leads = await db.scalar(
        select(func.count(CustomerModel.id)).where(
            CustomerModel.tenant_id == tenant_id,
            CustomerModel.lead_score >= 80,
            CustomerModel.is_deleted.is_(False),
        )
    ) or 0

    avg_health = await db.scalar(
        select(func.avg(CustomerModel.health_score)).where(
            CustomerModel.tenant_id == tenant_id,
            CustomerModel.is_deleted.is_(False),
        )
    ) or 0.0

    avg_churn = await db.scalar(
        select(func.avg(CustomerModel.churn_probability)).where(
            CustomerModel.tenant_id == tenant_id,
            CustomerModel.is_deleted.is_(False),
        )
    ) or 0.0

    total_ltv = await db.scalar(
        select(func.sum(CustomerModel.lifetime_value)).where(
            CustomerModel.tenant_id == tenant_id,
            CustomerModel.status == "active",
            CustomerModel.is_deleted.is_(False),
        )
    ) or 0.0

    # Top 5 at-risk customers
    risk_result = await db.execute(
        select(CustomerModel).where(
            CustomerModel.tenant_id == tenant_id,
            CustomerModel.churn_probability > 0.5,
            CustomerModel.is_deleted.is_(False),
        ).order_by(CustomerModel.churn_probability.desc()).limit(5)
    )
    risk_customers = risk_result.scalars().all()

    # Top 5 hot leads
    leads_result = await db.execute(
        select(CustomerModel).where(
            CustomerModel.tenant_id == tenant_id,
            CustomerModel.lead_score >= 80,
            CustomerModel.is_deleted.is_(False),
        ).order_by(CustomerModel.lead_score.desc()).limit(5)
    )
    hot_lead_customers = leads_result.scalars().all()

    # Pending recommendations
    pending_recs = await db.scalar(
        select(func.count(RecommendationModel.id)).where(
            RecommendationModel.tenant_id == tenant_id,
            RecommendationModel.status == "Pending",
        )
    ) or 0

    accepted_rev = await db.scalar(
        select(func.sum(RecommendationModel.expected_revenue)).where(
            RecommendationModel.tenant_id == tenant_id,
            RecommendationModel.status == "Accepted",
        )
    ) or 0.0

    return {
        "total_customers": total,
        "active_customers": active,
        "at_risk_count": at_risk_count,
        "hot_leads": hot_leads,
        "avg_health": round(float(avg_health), 1),
        "avg_churn": round(float(avg_churn), 3),
        "revenue_forecast": round(float(total_ltv), 2),
        "pending_recommendations": pending_recs,
        "accepted_revenue": round(float(accepted_rev), 2),
        "at_risk_customers": [
            {
                "name": f"{c.first_name} {c.last_name}",
                "company": c.company,
                "churn_probability": c.churn_probability,
                "health_score": c.health_score,
                "status": c.status,
            }
            for c in risk_customers
        ],
        "hot_lead_customers": [
            {
                "name": f"{c.first_name} {c.last_name}",
                "company": c.company,
                "lead_score": c.lead_score,
                "status": c.status,
            }
            for c in hot_lead_customers
        ],
    }


def format_crm_context_as_text(ctx: dict) -> str:
    """Convert context dict to a clear prompt string for the LLM."""
    at_risk_lines = "\n".join(
        f"  - {c['name']} at {c['company']}: {c['churn_probability']*100:.0f}% churn, health {c['health_score']:.0f}/100"
        for c in ctx["at_risk_customers"]
    )
    lead_lines = "\n".join(
        f"  - {c['name']} at {c['company']}: lead score {c['lead_score']}/100"
        for c in ctx["hot_lead_customers"]
    )
    return f"""
=== LIVE CRM DATA (Miracle Birds) ===
Total Customers: {ctx['total_customers']}
Active Customers: {ctx['active_customers']}
At-Risk Customers (churn > 50%): {ctx['at_risk_count']}
Hot Leads (score ≥ 80): {ctx['hot_leads']}
Average Health Score: {ctx['avg_health']}/100
Average Churn Probability: {ctx['avg_churn']*100:.1f}%
Revenue Forecast (Active LTV): ${ctx['revenue_forecast']:,.2f}
Pending AI Recommendations: {ctx['pending_recommendations']}
Revenue from Accepted Recommendations: ${ctx['accepted_revenue']:,.2f}

Top At-Risk Customers:
{at_risk_lines or '  None'}

Top Hot Leads:
{lead_lines or '  None'}
======================================
"""


async def call_llm(
    system_prompt: str,
    user_message: str,
    fallback_fn=None,
    max_tokens: int = 600,
    temperature: float = 0.6,
    model: str | None = None,
) -> str:
    """
    Call DeepSeek V4 Flash Free via opencode.ai.
    If the API fails, calls fallback_fn(user_message) if provided.
    """
    payload = {
        "model": model or FREE_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "MiracleBirds/1.0",
    }
    async with httpx.AsyncClient(timeout=45.0) as client:
        try:
            r = await client.post(OPENCODE_API_URL, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
            msg_obj = data["choices"][0]["message"]
            content = (msg_obj.get("content") or "").strip()
            if not content:
                content = (msg_obj.get("reasoning_content") or "").strip()
            if content:
                return content
        except Exception as e:
            print(f"[AI Engine] LLM call failed: {e}")

    if fallback_fn:
        return fallback_fn(user_message)
    return "I couldn't generate a response right now. Please try again shortly."


async def crm_chat(
    user_message: str,
    tenant_id,
    db: AsyncSession,
    model: str | None = None,
) -> str:
    """
    Full CRM-guarded AI chat pipeline:
    1. Guardrail check
    2. DB context fetch
    3. LLM call with CRM system prompt
    4. Smart data-driven fallback
    """
    # Step 1: Guardrail + prompt injection firewall
    from app.core.security_client import scan_prompt_injection

    injection = await scan_prompt_injection(user_message, tenant_id=str(tenant_id))
    if injection.get("blocked"):
        return (
            "Your message was blocked by the security firewall due to a potential "
            "prompt injection attempt. Please rephrase your CRM question."
        )

    if _is_blocked(user_message):
        return _guardrail_response()

    # Step 2: Fetch live CRM context
    ctx = await build_crm_context(tenant_id, db)
    context_text = format_crm_context_as_text(ctx)

    # Step 3: Build system prompt with guardrails + live data
    system_prompt = CRM_SYSTEM_GUARD + "\n" + context_text

    # Step 4: Fallback function using ctx
    def smart_fallback(msg: str) -> str:
        msg_lower = msg.lower()
        at_risk_names = ", ".join(
            f"{c['name']} at {c['company']} ({c['churn_probability']*100:.0f}%)"
            for c in ctx["at_risk_customers"]
        )
        lead_names = ", ".join(
            f"{c['name']} at {c['company']} (score {c['lead_score']})"
            for c in ctx["hot_lead_customers"]
        )

        if any(k in msg_lower for k in ["attention", "risk", "churn"]):
            return (
                f"Based on your live CRM data, these customers need immediate attention: "
                f"{at_risk_names or 'None flagged'}. "
                f"I recommend triggering the 'Churn Prevention Email' workflow or assigning a dedicated CSM."
            )
        elif any(k in msg_lower for k in ["lead", "hot", "prospect"]):
            return (
                f"Your top hot leads are: {lead_names or 'None at score ≥ 80'}. "
                f"These accounts have the highest lead scores and are ready for upsell outreach."
            )
        elif any(k in msg_lower for k in ["revenue", "forecast", "arr", "mrr", "ltv"]):
            return (
                f"Your active customer revenue forecast (total LTV) is ${ctx['revenue_forecast']:,.2f}. "
                f"Accepted AI recommendations have unlocked ${ctx['accepted_revenue']:,.2f} in additional pipeline."
            )
        elif any(k in msg_lower for k in ["health", "score", "engagement"]):
            return (
                f"Average customer health score across your {ctx['total_customers']} accounts is "
                f"{ctx['avg_health']}/100. "
                f"{ctx['at_risk_count']} customers are in the danger zone (health < 50)."
            )
        elif any(k in msg_lower for k in ["recommend", "action", "next", "suggest"]):
            return (
                f"You have {ctx['pending_recommendations']} pending AI recommendations. "
                f"Top next-best actions include upsell calls for hot leads and churn prevention outreach "
                f"for the {ctx['at_risk_count']} at-risk accounts."
            )
        else:
            return (
                f"Your CRM summary: {ctx['total_customers']} total customers, "
                f"{ctx['at_risk_count']} at churn risk, {ctx['hot_leads']} hot leads, "
                f"avg health score {ctx['avg_health']}/100, "
                f"revenue forecast ${ctx['revenue_forecast']:,.2f}. "
                "Ask me about specific customers, churn risk, leads, or revenue for details."
            )

    return await call_llm(system_prompt, user_message, fallback_fn=smart_fallback, model=model)


async def analyze_meeting_transcript(
    transcript: str,
    customer_name: str,
    company: str,
    meeting_title: str = "Client Call",
) -> dict:
    """
    Analyze a meeting transcript using the free LLM.
    Returns: {summary, sentiment, action_items, key_topics}
    """
    system_prompt = """You are a B2B CRM meeting analyst for an enterprise SaaS company.
Analyze the meeting transcript and return a JSON object with these EXACT fields:
{
  "summary": "2-3 sentence summary of the meeting",
  "sentiment": "positive|neutral|negative",
  "action_items": ["item1", "item2", "item3"],
  "key_topics": ["topic1", "topic2"],
  "churn_signal": "high|medium|low",
  "upsell_opportunity": true or false
}
Only return valid JSON. No markdown. No explanation."""

    user_msg = f"""
Meeting: {meeting_title}
Customer: {customer_name} at {company}
Transcript:
{transcript[:3000]}
"""

    import json

    def fallback(msg: str) -> str:
        # Keyword-based analysis fallback
        txt = transcript.lower()
        sentiment = "positive"
        churn_signal = "low"
        upsell = False

        if any(w in txt for w in ["cancel", "cancel", "leaving", "competitor", "unhappy", "disappointed"]):
            sentiment = "negative"
            churn_signal = "high"
        elif any(w in txt for w in ["concern", "issue", "problem", "slow", "bug"]):
            sentiment = "neutral"
            churn_signal = "medium"

        if any(w in txt for w in ["upgrade", "expand", "more seats", "enterprise", "additional"]):
            upsell = True

        result = {
            "summary": f"Meeting with {customer_name} at {company} covered key account topics. "
                       f"Customer expressed {'concerns that require follow-up' if sentiment != 'positive' else 'satisfaction with the platform'}.",
            "sentiment": sentiment,
            "action_items": [
                f"Follow up with {customer_name} within 48 hours",
                "Share relevant product documentation",
                "Update CRM with meeting outcome",
            ],
            "key_topics": ["Account review", "Product usage"],
            "churn_signal": churn_signal,
            "upsell_opportunity": upsell,
        }
        return json.dumps(result)

    raw = await call_llm(system_prompt, user_msg, fallback_fn=fallback, max_tokens=400, temperature=0.3)

    # Parse JSON response
    try:
        # Strip markdown if present
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(clean)
    except Exception:
        # If JSON parsing fails, use fallback directly
        import json as _json
        return _json.loads(fallback(""))


async def generate_recommendation_reason(
    customer_name: str,
    company: str,
    churn_prob: float,
    health_score: float,
    lead_score: int,
    action_type: str,
    expected_revenue: float,
) -> str:
    """Generate a specific business reason for an AI recommendation."""
    system_prompt = """You are a CRM intelligence engine. Write a concise 2-sentence 
business justification for the recommended sales/CSM action. 
Be specific, use the provided metrics, and be action-oriented. No lists."""

    user_msg = (
        f"Customer: {customer_name} at {company}\n"
        f"Churn Probability: {churn_prob*100:.0f}%\n"
        f"Health Score: {health_score:.0f}/100\n"
        f"Lead Score: {lead_score}/100\n"
        f"Recommended Action: {action_type}\n"
        f"Expected Revenue Impact: ${expected_revenue:,.0f}\n"
        "Generate a business justification for this action."
    )

    def fallback(msg: str) -> str:
        risk = "high" if churn_prob > 0.6 else "moderate" if churn_prob > 0.3 else "low"
        return (
            f"{customer_name} at {company} shows {risk} churn risk ({churn_prob*100:.0f}%) "
            f"with a health score of {health_score:.0f}/100, indicating {action_type.lower()} is critical. "
            f"This action is projected to preserve or unlock ${expected_revenue:,.0f} in ARR."
        )

    return await call_llm(system_prompt, user_msg, fallback_fn=fallback, max_tokens=150, temperature=0.4)
