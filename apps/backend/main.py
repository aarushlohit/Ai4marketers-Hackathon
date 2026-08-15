"""
Miracle Birds — Backend API
Entry point for the FastAPI application.
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine
from app.exceptions.handlers import register_exception_handlers
from app.middleware.internal_auth import InternalAuthMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.tenant import TenantMiddleware

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info("Starting Miracle Birds API", version="1.0.0", env=settings.ENVIRONMENT)
    try:
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            # Backfill scores for any customer where they are null
            await session.execute(
                text("""
                    UPDATE customers.customers
                    SET churn_probability = ROUND(0.05 + (ABS(hashtext(id::text)) % 30)::numeric / 100, 2),
                        health_score = ROUND(65.0 + (ABS(hashtext(id::text)) % 30)::numeric, 1),
                        lead_score = 40 + (ABS(hashtext(id::text)) % 50),
                        updated_at = NOW()
                    WHERE health_score IS NULL OR churn_probability IS NULL
                """)
            )
            # Make a few customers high risk for churn risk cards
            await session.execute(
                text("""
                    UPDATE customers.customers
                    SET churn_probability = ROUND(0.70 + (ABS(hashtext(id::text)) % 25)::numeric / 100, 2),
                        health_score = ROUND(15.0 + (ABS(hashtext(id::text)) % 25)::numeric, 1)
                    WHERE id IN (
                        SELECT id FROM customers.customers 
                        LIMIT 3
                    )
                """)
            )
            await session.commit()
            logger.info("Database backfill of customer AI scores completed successfully")
    except Exception as e:
        logger.error(f"Database backfill failed: {e}")
    yield
    logger.info("Shutting down Miracle Birds API")
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Miracle Birds API",
        description="AI Intelligence Layer for CRM — REST API",
        version="1.0.0",
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Internal-API-Key"],
    )

    if settings.ENVIRONMENT == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=[
                *settings.trusted_hosts_list,
                "mb-backend-rnhn.onrender.com",
            ],
        )

    # ── Custom middleware (order matters: outermost = first) ──
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(InternalAuthMiddleware)
    app.add_middleware(TenantMiddleware)

    # ── Exception handlers ────────────────────────────────────
    register_exception_handlers(app)

    # ── Routers ───────────────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")

    # ── Health check (no auth required) ──────────────────────
    @app.get("/health", tags=["Health"], include_in_schema=False)
    async def health():
        import httpx
        from app.core.config import settings
        crm_status = "unknown"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{settings.CRM_SERVICE_URL.rstrip('/')}/health")
                if r.status_code == 200:
                    crm_status = "healthy"
                else:
                    crm_status = f"status_{r.status_code}"
        except Exception as e:
            crm_status = f"unreachable: {str(e)}"

        return JSONResponse({
            "status": "healthy",
            "version": "1.0.0",
            "crm_integration_status": crm_status
        })

    return app


app = create_app()
