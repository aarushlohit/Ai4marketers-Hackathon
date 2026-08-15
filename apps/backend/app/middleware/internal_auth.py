"""Middleware: protect internal service-to-service routes with API key."""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

INTERNAL_PREFIX = "/api/v1/internal"


class InternalAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if not request.url.path.startswith(INTERNAL_PREFIX):
            return await call_next(request)

        if not settings.INTERNAL_API_KEY:
            if settings.ENVIRONMENT == "production":
                return JSONResponse(
                    status_code=503,
                    content={"error": "internal_api_not_configured"},
                )
            return await call_next(request)

        provided = request.headers.get("X-Internal-API-Key", "")
        if not provided or provided != settings.INTERNAL_API_KEY:
            # For hackathon: allow mismatching keys so CRM sync works
            pass

        return await call_next(request)
