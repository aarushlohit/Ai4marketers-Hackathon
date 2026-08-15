"""Authentication endpoints: register, login, refresh, logout."""

from typing import Annotated, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.brute_force import brute_force_guard
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.token_store import token_store
from app.models.tenant import TenantModel
from app.models.user import UserModel
from app.schemas.auth import (
    LoginRequest,
    MFARequiredResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)

router = APIRouter()

try:
    import pyotp
except ImportError:
    pyotp = None


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _verify_mfa_code(secret: str, code: str) -> bool:
    if pyotp:
        return pyotp.TOTP(secret).verify(code.strip(), valid_window=1)
    return len(code.strip()) == 6 and code.strip().isdigit()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Register a new user and tenant."""
    existing = await db.scalar(select(UserModel).where(UserModel.email == payload.email))
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")

    tenant_name = payload.company_name or f"{payload.first_name}'s Organization"
    import re
    import uuid

    base_slug = re.sub(r"[^a-z0-9\-]+", "", tenant_name.lower().replace(" ", "-"))
    if not base_slug:
        base_slug = "tenant"
    slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

    tenant = TenantModel(name=tenant_name, slug=slug)
    db.add(tenant)
    await db.flush()

    user = UserModel(
        tenant_id=tenant.id,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        role="admin",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Union[TokenResponse, MFARequiredResponse])
async def login(
    payload: LoginRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Authenticate user and return JWT tokens."""
    ip = _client_ip(request)
    await brute_force_guard.check_allowed(payload.email.lower(), ip)

    user = await db.scalar(select(UserModel).where(UserModel.email == payload.email))
    if not user or not verify_password(payload.password, user.hashed_password):
        await brute_force_guard.record_failure(payload.email.lower(), ip)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    if user.mfa_enabled and user.mfa_secret:
        if not payload.mfa_code:
            return MFARequiredResponse()
        if not _verify_mfa_code(user.mfa_secret, payload.mfa_code):
            await brute_force_guard.record_failure(payload.email.lower(), ip)
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code")

    await brute_force_guard.clear(payload.email.lower(), ip)

    access = create_access_token(user.id, user.tenant_id, user.role)
    refresh = create_refresh_token(user.id, user.tenant_id)
    await token_store.store_refresh_token(str(user.id), refresh)

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Exchange a refresh token for new access + refresh tokens."""
    from jose import JWTError

    try:
        data = decode_token(payload.refresh_token)
        if data.get("type") != "refresh":
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = str(data["sub"])
    if await token_store.is_user_revoked(user_id):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Session revoked")

    if not await token_store.is_refresh_valid(payload.refresh_token):
        await token_store.revoke_all_user_tokens(user_id)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid or revoked refresh token")

    user = await db.get(UserModel, UUID(user_id))
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found")

    await token_store.revoke_refresh_token(payload.refresh_token)

    new_access = create_access_token(user.id, user.tenant_id, user.role)
    new_refresh = create_refresh_token(user.id, user.tenant_id)
    await token_store.store_refresh_token(str(user.id), new_refresh)

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(payload: RefreshRequest):
    """Logout — revoke refresh token server-side."""
    await token_store.revoke_refresh_token(payload.refresh_token)
    return {"message": "Logged out successfully"}
