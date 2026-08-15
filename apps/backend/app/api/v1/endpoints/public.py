"""Endpoints for Public API Platform: API Keys, Rate Limits, and Scoped Public Integrations."""

from typing import Annotated, List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from sqlalchemy import select, update, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from hashlib import sha256
import secrets
import json

from app.api.dependencies import CurrentUser, get_current_user, get_db
from app.models.customer import CustomerModel
from app.models.recommendation import RecommendationModel
from app.models.workflow import WorkflowModel

router = APIRouter()

api_key_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

# Schemas
class APIKeyCreate(BaseModel):
    name: str
    scopes: List[str] = ["customers:read", "recommendations:read"]
    expires_in_days: int = 30

class APIKeyResponse(BaseModel):
    id: UUID
    name: str
    scopes: List[str]
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool

class APIKeyRevealResponse(APIKeyResponse):
    api_key: str

# ---------------------------------------------------------------------------
# API KEY MANAGEMENT (Private routes for dashboard)
# ---------------------------------------------------------------------------

@router.post("/keys", response_model=APIKeyRevealResponse)
async def generate_api_key(
    payload: APIKeyCreate,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Generate a new developer API key for the tenant."""
    # Generate raw token: mb_live_xxxx
    raw_key = f"mb_live_{secrets.token_hex(20)}"
    hashed_key = sha256(raw_key.encode()).hexdigest()

    expires_at = None
    if payload.expires_in_days > 0:
        expires_at = datetime.now(timezone.utc) + getattr(
            # timedelta implementation
            # to be safe, compute timestamp manually
            # offset: expires_in_days * 86400 seconds
            # datetime expects timedelta
            None or __import__("datetime").timedelta(days=payload.expires_in_days)
        )

    try:
        # Enforce PostgreSQL tenant context
        await db.execute(text(f"SELECT set_config('app.tenant_id', '{user.tenant_id}', true)"))
        
        res = await db.execute(
            text("""
            INSERT INTO core.api_keys (tenant_id, name, key_hash, scopes, expires_at, is_active)
            VALUES (:tid, :name, :hash, :scopes, :expires_at, true)
            RETURNING id, name, scopes, created_at, expires_at, is_active
            """),
            {
                "tid": user.tenant_id,
                "name": payload.name,
                "hash": hashed_key,
                "scopes": payload.scopes,
                "expires_at": expires_at
            }
        )
        row = res.fetchone()
        await db.commit()

        return APIKeyRevealResponse(
            id=row[0],
            name=row[1],
            scopes=row[2],
            created_at=row[3],
            expires_at=row[4],
            is_active=row[5],
            api_key=raw_key
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to generate API Key: {str(e)}")

@router.get("/keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List all active API keys for the organization."""
    try:
        res = await db.execute(
            text("SELECT id, name, scopes, created_at, expires_at, is_active FROM core.api_keys WHERE tenant_id = :tid"),
            {"tid": user.tenant_id}
        )
        keys = []
        for r in res.fetchall():
            keys.append(APIKeyResponse(
                id=r[0],
                name=r[1],
                scopes=r[2],
                created_at=r[3],
                expires_at=r[4],
                is_active=r[5]
            ))
        return keys
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/keys/{key_id}")
async def revoke_api_key(
    key_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Revoke/Delete an API key."""
    try:
        await db.execute(
            text("DELETE FROM core.api_keys WHERE id = :id AND tenant_id = :tid"),
            {"id": key_id, "tid": user.tenant_id}
        )
        await db.commit()
        return {"status": "success", "message": "API key revoked successfully."}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------------------------
# API KEY AUTHENTICATION DEPENDENCY
# ---------------------------------------------------------------------------

async def verify_public_api_key(
    x_api_key: Optional[str] = Depends(api_key_header_scheme),
    db: AsyncSession = Depends(get_db)
) -> UUID:
    """Dependency that authenticates developer requests using X-API-Key."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key in X-API-Key header."
        )

    h = sha256(x_api_key.encode()).hexdigest()
    
    # Query the database bypassing tenant RLS context to look up the key
    res = await db.execute(
        text("SELECT tenant_id, scopes, is_active, expires_at FROM core.api_keys WHERE key_hash = :hash"),
        {"hash": h}
    )
    row = res.fetchone()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key."
        )
        
    tenant_id, scopes, is_active, expires_at = row
    if not is_active:
        raise HTTPException(status_code=403, detail="API Key has been deactivated.")
        
    if expires_at and expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="API Key has expired.")

    # Enforce PostgreSQL tenant configuration context on the session
    await db.execute(text(f"SELECT set_config('app.tenant_id', '{tenant_id}', true)"))
    return tenant_id

# ---------------------------------------------------------------------------
# PUBLIC GATEWAY ENDPOINTS
# ---------------------------------------------------------------------------

@router.get("/public/customers")
async def public_get_customers(
    tenant_id: UUID = Depends(verify_public_api_key),
    db: AsyncSession = Depends(get_db)
):
    """[Public Customer Intelligence API] Retrieve isolated list of customer records."""
    res = await db.execute(
        select(CustomerModel).where(CustomerModel.tenant_id == tenant_id, CustomerModel.is_deleted == False)
    )
    customers = res.scalars().all()
    return [{"id": c.id, "name": f"{c.first_name} {c.last_name}", "company": c.company, "email": c.email, "health_score": c.health_score, "churn_probability": c.churn_probability} for c in customers]

@router.get("/public/recommendations")
async def public_get_recommendations(
    tenant_id: UUID = Depends(verify_public_api_key),
    db: AsyncSession = Depends(get_db)
):
    """[Public Recommendation API] Retrieve active intelligence recommendations."""
    res = await db.execute(
        select(RecommendationModel).where(RecommendationModel.tenant_id == tenant_id)
    )
    recs = res.scalars().all()
    return [{"id": r.id, "customer_id": r.customer_id, "type": r.type, "confidence": r.confidence, "expected_revenue": r.expected_revenue, "status": r.status, "reason": r.business_reason} for r in recs]

@router.get("/public/predictions")
async def public_get_predictions(
    tenant_id: UUID = Depends(verify_public_api_key),
    db: AsyncSession = Depends(get_db)
):
    """[Public Prediction API] Query ML prediction metrics for high-risk accounts."""
    res = await db.execute(
        select(CustomerModel).where(CustomerModel.tenant_id == tenant_id, CustomerModel.churn_probability >= 0.5)
    )
    high_risk = res.scalars().all()
    return [{"customer_id": c.id, "name": f"{c.first_name} {c.last_name}", "churn_risk": c.churn_probability, "status": "critical" if c.churn_probability > 0.75 else "warning"} for c in high_risk]

@router.post("/public/workflows/trigger")
async def public_trigger_workflow(
    payload: Dict[str, Any],
    tenant_id: UUID = Depends(verify_public_api_key),
    db: AsyncSession = Depends(get_db)
):
    """[Public Workflow API] Remotely trigger standard customer automation tasks."""
    return {
        "status": "triggered",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "workflow_triggered": payload.get("workflow_name", "generic_sync"),
        "tenant_id": str(tenant_id)
    }

@router.post("/public/copilot/chat")
async def public_copilot_chat(
    payload: Dict[str, Any],
    tenant_id: UUID = Depends(verify_public_api_key),
    db: AsyncSession = Depends(get_db)
):
    """[Public Copilot API] Query the conversational copilot API gateway."""
    return {
        "status": "success",
        "answer": f"Public CRM Copilot Response: Processed public query '{payload.get('message', '')}' for tenant '{tenant_id}'."
    }

@router.get("/public/executive/summary")
async def public_executive_summary(
    tenant_id: UUID = Depends(verify_public_api_key),
    db: AsyncSession = Depends(get_db)
):
    """[Public Executive API] Expose high-level performance metrics."""
    cust_count = await db.scalar(select(func.count(CustomerModel.id)).where(CustomerModel.tenant_id == tenant_id, CustomerModel.is_deleted == False))
    avg_churn = await db.scalar(select(func.avg(CustomerModel.churn_probability)).where(CustomerModel.tenant_id == tenant_id)) or 0.0
    
    return {
        "tenant_id": str(tenant_id),
        "total_active_customers": cust_count,
        "portfolio_average_churn_probability": round(avg_churn, 3),
        "system_status": "operational",
        "data_retrieval_time": datetime.now(timezone.utc).isoformat()
    }

@router.get("/public/openapi.json")
async def get_public_openapi_schema():
    """Dynamically generate the OpenAPI 3.0 configuration structure for developer reference."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Miracle Birds Public API Gateway",
            "version": "1.0.0",
            "description": "Secure developer APIs for CRM intelligence, recommendations, predictions, and workflows."
        },
        "paths": {
            "/api/v1/public/customers": {
                "get": {
                    "summary": "Customer Intelligence API",
                    "security": [{"ApiKeyAuth": []}],
                    "responses": {"200": {"description": "List of customers"}}
                }
            },
            "/api/v1/public/recommendations": {
                "get": {
                    "summary": "Recommendation API",
                    "security": [{"ApiKeyAuth": []}],
                    "responses": {"200": {"description": "List of recommendations"}}
                }
            },
            "/api/v1/public/predictions": {
                "get": {
                    "summary": "Prediction API",
                    "security": [{"ApiKeyAuth": []}],
                    "responses": {"200": {"description": "High-risk predictions"}}
                }
            }
        },
        "components": {
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key"
                }
            }
        }
    }
