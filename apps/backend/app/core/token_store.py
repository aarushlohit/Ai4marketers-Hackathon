"""Redis-backed refresh token store with revocation support."""

import hashlib
import secrets
from datetime import timedelta

import redis.asyncio as aioredis

from app.core.config import settings

REFRESH_PREFIX = "refresh:"
REVOKED_PREFIX = "revoked:"
REFRESH_TTL = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class TokenStore:
    def __init__(self):
        self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        self._memory: dict[str, str] = {}
        self._revoked: set[str] = set()

    async def store_refresh_token(self, user_id: str, token: str) -> None:
        key = f"{REFRESH_PREFIX}{_hash_token(token)}"
        try:
            await self.redis.setex(key, int(REFRESH_TTL.total_seconds()), user_id)
        except Exception:
            self._memory[key] = user_id

    async def is_refresh_valid(self, token: str) -> bool:
        key = f"{REFRESH_PREFIX}{_hash_token(token)}"
        revoked = f"{REVOKED_PREFIX}{_hash_token(token)}"
        try:
            if await self.redis.exists(revoked):
                return False
            return bool(await self.redis.exists(key))
        except Exception:
            if revoked in self._revoked:
                return False
            return key in self._memory

    async def revoke_refresh_token(self, token: str) -> None:
        key = f"{REFRESH_PREFIX}{_hash_token(token)}"
        revoked = f"{REVOKED_PREFIX}{_hash_token(token)}"
        try:
            await self.redis.delete(key)
            await self.redis.setex(revoked, int(REFRESH_TTL.total_seconds()), "1")
        except Exception:
            self._memory.pop(key, None)
            self._revoked.add(revoked)

    async def revoke_all_user_tokens(self, user_id: str) -> None:
        try:
            await self.redis.setex(
                f"user_revoked:{user_id}", 86400 * 7, secrets.token_hex(16)
            )
        except Exception:
            self._memory.pop(f"user_revoked:{user_id}", None)
            self._memory[f"user_revoked:{user_id}"] = "1"

    async def is_user_revoked(self, user_id: str) -> bool:
        try:
            return bool(await self.redis.exists(f"user_revoked:{user_id}"))
        except Exception:
            return f"user_revoked:{user_id}" in self._memory


token_store = TokenStore()
