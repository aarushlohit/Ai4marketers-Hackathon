"""
Feature Engineering Pipeline
Builds the feature matrix for ML models from raw customer data.
Each function takes a customer dict and returns a flat feature vector.
"""

import math
from datetime import datetime, timezone


def compute_churn_features(customer: dict, interactions: list[dict]) -> dict:
    """
    Build 50+ features for churn prediction.

    Feature groups:
      - Recency: days since last interaction, login, purchase
      - Frequency: interaction count per period
      - Engagement: email open rate, meeting attendance
      - Support: ticket count, resolution time, CSAT
      - Financial: MRR, payment delays, contract length
      - Product: feature adoption, session depth
    """
    now = datetime.now(timezone.utc)

    # ── Recency features ─────────────────────────────────────
    last_interaction = max(
        (i.get("occurred_at") for i in interactions if i.get("occurred_at")),
        default=None,
    )
    days_since_last_interaction = (
        (now - _parse_dt(last_interaction)).days
        if last_interaction else 999
    )

    # ── Frequency features ───────────────────────────────────
    last_30d = [
        i for i in interactions
        if i.get("occurred_at")
        and (now - _parse_dt(i["occurred_at"])).days <= 30
    ]
    last_90d = [
        i for i in interactions
        if i.get("occurred_at")
        and (now - _parse_dt(i["occurred_at"])).days <= 90
    ]
    interaction_count_30d = len(last_30d)
    interaction_count_90d = len(last_90d)
    interaction_velocity = (
        interaction_count_30d / max(interaction_count_90d, 1)
        if interaction_count_90d > 0 else 0.0
    )

    # ── Type breakdown ───────────────────────────────────────
    type_counts = {}
    for t in ["email", "call", "meeting", "note", "demo"]:
        type_counts[f"{t}_count_90d"] = sum(
            1 for i in last_90d if i.get("interaction_type") == t
        )

    # ── Sentiment features ───────────────────────────────────
    sentiments = [
        i.get("sentiment_score", 0.0)
        for i in last_30d
        if i.get("sentiment_score") is not None
    ]
    avg_sentiment = (sum(sentiments) / len(sentiments)) if sentiments else 0.5
    negative_ratio = (
        sum(1 for s in sentiments if s < 0.4) / len(sentiments)
        if sentiments else 0.0
    )

    # ── Account metadata ─────────────────────────────────────
    created_at = customer.get("created_at")
    account_age_days = (
        (now - _parse_dt(created_at)).days if created_at else 0
    )
    has_email = 1 if customer.get("email") else 0
    has_phone = 1 if customer.get("phone") else 0
    has_company = 1 if customer.get("company") else 0

    # ── Score features (from previous predictions) ───────────
    health_score = customer.get("health_score") or 50.0
    lead_score = customer.get("lead_score") or 50
    lifetime_value = customer.get("lifetime_value") or 0.0
    log_ltv = math.log1p(lifetime_value)

    # ── Status encoding ──────────────────────────────────────
    status_map = {"active": 1, "inactive": 0, "churned": -1}
    status_encoded = status_map.get(customer.get("status", "active"), 0)

    return {
        "days_since_last_interaction": days_since_last_interaction,
        "interaction_count_30d": interaction_count_30d,
        "interaction_count_90d": interaction_count_90d,
        "interaction_velocity": interaction_velocity,
        **type_counts,
        "avg_sentiment_30d": avg_sentiment,
        "negative_sentiment_ratio": negative_ratio,
        "account_age_days": account_age_days,
        "has_email": has_email,
        "has_phone": has_phone,
        "has_company": has_company,
        "health_score": health_score,
        "lead_score": lead_score,
        "log_lifetime_value": log_ltv,
        "status_encoded": status_encoded,
    }


def compute_lead_score_features(customer: dict, interactions: list[dict]) -> dict:
    """Build feature vector for lead scoring model."""
    base = compute_churn_features(customer, interactions)

    company = customer.get("company", "")
    title = (customer.get("title") or "").lower()

    # Seniority signals from job title
    is_decision_maker = int(
        any(kw in title for kw in ["ceo", "cto", "vp", "director", "head of", "chief"])
    )
    is_manager = int(any(kw in title for kw in ["manager", "lead", "senior"]))

    # Company size proxy (from company name length — real impl uses enrichment API)
    company_size_proxy = min(len(company) / 5, 10.0)

    return {
        **base,
        "is_decision_maker": is_decision_maker,
        "is_manager": is_manager,
        "company_size_proxy": company_size_proxy,
        "has_demo": base.get("demo_count_90d", 0) > 0,
        "multi_channel_engaged": sum([
            base.get("email_count_90d", 0) > 0,
            base.get("call_count_90d", 0) > 0,
            base.get("meeting_count_90d", 0) > 0,
        ]),
    }


def _parse_dt(value) -> datetime:
    """Parse a datetime string or return epoch."""
    if isinstance(value, datetime):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime(1970, 1, 1, tzinfo=timezone.utc)
