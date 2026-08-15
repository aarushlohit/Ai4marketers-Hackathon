"""Redis-backed brute force protection for authentication endpoints."""

import time

import redis.asyncio as aioredis
from fastapi import HTTPException, status

from app.core.config import settings

MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 900  # 15 minutes
WINDOW_SECONDS = 900


class BruteForceGuard:
    def __init__(self):
        self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    def _keys(self, identifier: str, ip: str) -> tuple[str, str]:
        return (
            f"login_fail:{identifier}",
            f"login_fail_ip:{ip}",
        )

    async def check_allowed(self, identifier: str, ip: str) -> None:
        try:
            for key in self._keys(identifier, ip):
                locked_until = await self.redis.get(f"{key}:lock")
                if locked_until and float(locked_until) > time.time():
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Too many failed login attempts. Try again later.",
                    )
        except HTTPException:
            raise
        except Exception:
            return

    async def record_failure(self, identifier: str, ip: str) -> None:
        try:
            for key in self._keys(identifier, ip):
                count = await self.redis.incr(key)
                if count == 1:
                    await self.redis.expire(key, WINDOW_SECONDS)
                if count >= MAX_ATTEMPTS:
                    await self.redis.setex(
                        f"{key}:lock",
                        LOCKOUT_SECONDS,
                        str(time.time() + LOCKOUT_SECONDS),
                    )
        except Exception:
            return

    async def clear(self, identifier: str, ip: str) -> None:
        try:
            for key in self._keys(identifier, ip):
                await self.redis.delete(key, f"{key}:lock")
        except Exception:
            return


brute_force_guard = BruteForceGuard()
