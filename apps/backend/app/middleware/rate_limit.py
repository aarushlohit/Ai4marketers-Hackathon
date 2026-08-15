"""Middleware: Redis-backed token-bucket rate limiting per tenant."""

import time

import redis.asyncio as aioredis
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

RATE_LIMITS = {
    "standard": 1000,
    "professional": 5000,
    "enterprise": 999999,
}
WINDOW_SECONDS = 3600


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip health and auth endpoints
        if request.url.path in ("/health",) or request.url.path.startswith("/api/v1/auth"):
            return await call_next(request)

        tenant_id = str(getattr(request.state, "tenant_id", "anonymous"))
        key = f"rate:{tenant_id}:{int(time.time() // WINDOW_SECONDS)}"
        limit = RATE_LIMITS["professional"]  # TODO: look up tenant plan

        try:
            count = await self.redis.incr(key)
            if count == 1:
                await self.redis.expire(key, WINDOW_SECONDS)
        except Exception:
            count = 1

        if count > limit:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "detail": "Rate limit exceeded. Try again later.",
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - count))
        return response
