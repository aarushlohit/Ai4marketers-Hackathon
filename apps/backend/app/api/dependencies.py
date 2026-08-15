"""Shared FastAPI dependencies: auth, pagination, DB session."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, set_rls_context
from app.core.security import decode_token

security = HTTPBearer(auto_error=False)

class CurrentUser:
    def __init__(self, user_id: UUID, tenant_id: UUID, role: str):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.role = role


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> CurrentUser:
    """Validate JWT token and return user context."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        payload = decode_token(credentials.credentials)
        return CurrentUser(
            user_id=UUID(payload["sub"]),
            tenant_id=UUID(payload["tenant_id"]),
            role=payload.get("role", "user"),
        )
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def require_role(*roles: str):
    """Factory for role-based access control dependencies."""
    async def check(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if user.role not in roles and user.role != "super_admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return check


class Pagination:
    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=50, ge=1, le=100),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size
