"""Middleware: extract tenant_id from JWT and set PostgreSQL RLS context."""

from uuid import UUID

from fastapi import Request, Response
from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import decode_token


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Extracts tenant_id from the Bearer token and attaches it to
    request.state so downstream dependencies can use it to set RLS.
    """

    SKIP_PATHS = {"/health", "/api/v1/auth/login", "/api/v1/auth/register",
                  "/api/v1/auth/refresh", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        authorization = request.headers.get("Authorization", "")
        if authorization.startswith("Bearer "):
            token = authorization.removeprefix("Bearer ")
            try:
                payload = decode_token(token)
                request.state.tenant_id = UUID(payload["tenant_id"])
                request.state.user_id = UUID(payload["sub"])
                request.state.role = payload.get("role", "user")
            except (JWTError, KeyError, ValueError):
                pass  # Auth dependency handles the 401

        return await call_next(request)
