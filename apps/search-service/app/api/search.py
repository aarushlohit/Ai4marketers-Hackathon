"""Search Service — Semantic Enterprise Search API.

Searches across customers, meetings, activities, emails, recommendations, and knowledge graph.
Returns ranked semantic results with relevance scores.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

router = APIRouter()

SEARCH_TYPES = ["customers", "meetings", "emails", "activities", "recommendations", "tickets", "all"]


class SearchRequest(BaseModel):
    query: str
    search_type: str = "all"
    filters: Dict[str, Any] = Field(default_factory=dict)
    limit: int = 20
    offset: int = 0
    min_relevance: float = 0.0


class SearchResult(BaseModel):
    id: str
    source_type: str
    title: str
    snippet: str
    relevance_score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    matched_terms: List[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: int
    search_type: str


@router.post("/query", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Execute a semantic search across the enterprise."""
    if request.search_type not in SEARCH_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid search type: {request.search_type}. Valid types: {', '.join(SEARCH_TYPES)}")

    query_terms = request.query.lower().split()
    results = []

    # Mock search across different data sources
    mock_data = _get_mock_search_data(request.search_type)

    for item in mock_data:
        content_lower = item["content"].lower()
        title_lower = item["title"].lower()

        # Calculate relevance score based on term matching
        matched_terms = []
        score = 0.0
        for term in query_terms:
            if term in title_lower:
                score += 0.4
                matched_terms.append(term)
            elif term in content_lower:
                score += 0.2
                matched_terms.append(term)

        if score > 0:
            score = min(1.0, score)
            if score >= request.min_relevance:
                # Generate snippet with context
                snippet = _generate_snippet(item["content"], query_terms)

                results.append(SearchResult(
                    id=item["id"],
                    source_type=item["source_type"],
                    title=item["title"],
                    snippet=snippet,
                    relevance_score=round(score, 3),
                    metadata=item.get("metadata", {}),
                    matched_terms=matched_terms,
                ))

    # Sort by relevance
    results.sort(key=lambda r: r.relevance_score, reverse=True)
    total = len(results)
    results = results[request.offset:request.offset + request.limit]

    return SearchResponse(
        query=request.query,
        results=results,
        total_results=total,
        search_time_ms=45,
        search_type=request.search_type,
    )


@router.post("/customers/{customer_id}", response_model=SearchResponse)
async def search_customer_context(customer_id: str, request: SearchRequest):
    """Search within a specific customer's context."""
    query_terms = request.query.lower().split()
    results = []

    # Mock customer-specific data
    mock_data = [
        {
            "id": f"email-{i}", "source_type": "email", "title": f"Email re: {request.query}",
            "content": f"Discussion regarding {request.query} with customer {customer_id}. Key points included pricing, timeline, and next steps.",
            "metadata": {"customer_id": customer_id, "date": "2026-07-15", "direction": "outbound"},
        }
        for i in range(3)
    ] + [
        {
            "id": f"meeting-{i}", "source_type": "meeting", "title": f"Meeting: {request.query} Review",
            "content": f"Quarterly review meeting with customer {customer_id}. Discussed {request.query}, product roadmap, and support needs.",
            "metadata": {"customer_id": customer_id, "date": "2026-07-10", "duration_min": 45},
        }
        for i in range(2)
    ]

    for item in mock_data:
        content_lower = item["content"].lower()
        score = 0.0
        for term in query_terms:
            if term in content_lower:
                score += 0.25
        if score > 0:
            results.append(SearchResult(
                id=item["id"],
                source_type=item["source_type"],
                title=item["title"],
                snippet=_generate_snippet(item["content"], query_terms),
                relevance_score=round(min(1.0, score), 3),
                metadata=item["metadata"],
                matched_terms=[t for t in query_terms if t in content_lower],
            ))

    results.sort(key=lambda r: r.relevance_score, reverse=True)
    return SearchResponse(
        query=request.query,
        results=results[:request.limit],
        total_results=len(results),
        search_time_ms=32,
        search_type=request.search_type,
    )


@router.post("/suggest", response_model=List[str])
async def suggest_queries(partial_query: str, limit: int = 5):
    """Get search query suggestions based on partial input."""
    suggestions = [
        f"customers with {partial_query}",
        f"meetings about {partial_query}",
        f"emails regarding {partial_query}",
        f"support tickets for {partial_query}",
        f"deals related to {partial_query}",
    ]
    return suggestions[:limit]


def _generate_snippet(content: str, query_terms: List[str], context_chars: int = 100) -> str:
    """Generate a relevant snippet with context around matched terms."""
    content_lower = content.lower()
    for term in query_terms:
        idx = content_lower.find(term)
        if idx != -1:
            start = max(0, idx - context_chars)
            end = min(len(content), idx + len(term) + context_chars)
            snippet = content[start:end]
            if start > 0:
                snippet = "..." + snippet
            if end < len(content):
                snippet = snippet + "..."
            return snippet
    return content[:200] + "..." if len(content) > 200 else content


def _get_mock_search_data(search_type: str) -> List[Dict[str, Any]]:
    """Get mock search data for different types."""
    all_data = [
        # Customers
        {"id": "cust-1", "source_type": "customer", "title": "Acme Corp", "content": "Enterprise customer in manufacturing sector. $500K ARR, 45 users. High satisfaction score of 92/100. Recent expansion opportunity identified.", "metadata": {"industry": "Manufacturing", "arr": 500000, "health": 92}},
        {"id": "cust-2", "source_type": "customer", "title": "TechStart Inc", "content": "Mid-market SaaS company. $120K ARR, 25 users. Recently upgraded to Enterprise plan. High growth potential with 30% MoM expansion.", "metadata": {"industry": "SaaS", "arr": 120000, "health": 88}},
        {"id": "cust-3", "source_type": "customer", "title": "GlobalBank", "content": "Financial services enterprise. $2M ARR, 500 users. Premium support tier. Complex regulatory requirements. Risk level: low.", "metadata": {"industry": "Financial Services", "arr": 2000000, "health": 95}},
        # Meetings
        {"id": "mtg-1", "source_type": "meeting", "title": "Q3 Business Review - Acme Corp", "content": "Quarterly review with Acme Corp. Customer expressed strong interest in AI Copilot module. Action item: schedule technical demo. Sentiment: positive.", "metadata": {"customer": "Acme Corp", "date": "2026-07-12", "sentiment": "positive"}},
        {"id": "mtg-2", "source_type": "meeting", "title": "Onboarding Session - TechStart", "content": "Enterprise onboarding session for TechStart Inc. Covered workflow automation and analytics dashboard. Customer requested additional training for team leads.", "metadata": {"customer": "TechStart Inc", "date": "2026-07-08", "sentiment": "neutral"}},
        # Emails
        {"id": "email-1", "source_type": "email", "title": "Contract Renewal - GlobalBank", "content": "Contract renewal discussion with GlobalBank. Terms: 3-year enterprise agreement with 15% annual increase. Legal review in progress.", "metadata": {"customer": "GlobalBank", "direction": "outbound", "date": "2026-07-14"}},
        {"id": "email-2", "source_type": "email", "title": "Support Escalation - Acme Corp", "content": "Customer reported critical performance issue affecting production environment. SLA impact: Level 1 breach. Engineering team engaged for root cause analysis.", "metadata": {"customer": "Acme Corp", "priority": "critical", "date": "2026-07-11"}},
        # Activities
        {"id": "act-1", "source_type": "activity", "title": "Product Demo - Workflow Module", "content": "Conducted live demo of Workflow Automation module for TechStart Inc. Three team leads attended. Follow-up scheduled for pricing discussion.", "metadata": {"customer": "TechStart Inc", "type": "demo", "date": "2026-07-09"}},
        {"id": "act-2", "source_type": "activity", "title": "Support Ticket Analysis", "content": "Analyzed support ticket trends for GlobalBank. Identified 15% increase in API-related tickets. Recommended proactive outreach and technical documentation update.", "metadata": {"type": "analysis", "date": "2026-07-07"}},
        # Recommendations
        {"id": "rec-1", "source_type": "recommendation", "title": "Upsell: AI Copilot for Acme Corp", "content": "Recommend introducing AI Copilot to Acme Corp based on 92 health score and expressed interest. Expected revenue: $75K ARR. Confidence: 85%.", "metadata": {"customer": "Acme Corp", "expected_revenue": 75000, "confidence": 0.85}},
        {"id": "rec-2", "source_type": "recommendation", "title": "Retention: Proactive Outreach for TechStart", "content": "TechStart Inc showing early signs of engagement decline. Recommend executive check-in and feature adoption workshop. Estimated churn reduction: 35%.", "metadata": {"customer": "TechStart Inc", "impact": "churn_reduction", "priority": "high"}},
        # Tickets
        {"id": "tkt-1", "source_type": "ticket", "title": "API Rate Limiting Issues", "content": "Multiple customers reporting API rate limiting during peak hours. Engineering team evaluating threshold adjustments. ETA for fix: 48 hours.", "metadata": {"priority": "high", "status": "in_progress", "customer_impact": "multiple"}},
        {"id": "tkt-2", "source_type": "ticket", "title": "Dashboard Loading Performance", "content": "Analytics dashboard taking >10 seconds to load for enterprise customers with 500+ users. Performance optimization in progress.", "metadata": {"priority": "medium", "status": "investigating"}},
    ]

    if search_type == "all":
        return all_data
    return [d for d in all_data if d["source_type"] == search_type]
