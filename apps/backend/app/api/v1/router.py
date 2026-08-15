"""Aggregates all v1 endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    analytics,
    auth,
    copilot,
    customers,
    integrations,
    internal,
    predictions,
    users,
    workflows,
    recommendations,
    feedback,
    meetings,
    executive,
    billing,
    marketplace,
    public,
    compliance,
    security,
    governance,
    learning,
)

api_router = APIRouter()

api_router.include_router(internal.router,    prefix="/internal",    tags=["Internal"])
api_router.include_router(auth.router,         prefix="/auth",         tags=["Authentication"])
api_router.include_router(customers.router,    prefix="/customers",    tags=["Customers"])
api_router.include_router(predictions.router,  prefix="/predictions",  tags=["Predictions"])
api_router.include_router(analytics.router,    prefix="/analytics",    tags=["Analytics"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])
api_router.include_router(copilot.router,      prefix="/copilot",      tags=["AI Copilot"])
api_router.include_router(users.router,        prefix="/users",        tags=["Users"])
api_router.include_router(workflows.router,    prefix="/workflows",    tags=["Workflows"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
api_router.include_router(feedback.router,     prefix="/feedback",     tags=["Feedback"])
api_router.include_router(meetings.router,     prefix="/meetings",     tags=["Meetings"])
api_router.include_router(executive.router,    prefix="/executive",    tags=["Executive"])
api_router.include_router(billing.router,      prefix="/billing",      tags=["Billing"])
api_router.include_router(marketplace.router,  prefix="/marketplace",  tags=["Marketplace"])
api_router.include_router(public.router,       prefix="/public",       tags=["Public API Gateway"])
api_router.include_router(compliance.router,   prefix="/compliance",   tags=["Compliance"])
api_router.include_router(security.router,     prefix="/security",     tags=["Security Center"])
api_router.include_router(governance.router,   prefix="/governance",   tags=["AI Governance"])
api_router.include_router(learning.router,     prefix="/learning",     tags=["Reinforcement Learning"])

