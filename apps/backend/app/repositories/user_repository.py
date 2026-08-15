"""User Repository — data access layer for user management."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserModel


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> UserModel | None:
        return await self.db.get(UserModel, user_id)

    async def get_by_email(self, email: str) -> UserModel | None:
        return await self.db.scalar(
            select(UserModel).where(UserModel.email == email)
        )

    async def get_by_tenant(self, tenant_id: UUID) -> list[UserModel]:
        results = await self.db.scalars(
            select(UserModel)
            .where(UserModel.tenant_id == tenant_id, UserModel.is_active.is_(True))
            .order_by(UserModel.created_at)
        )
        return list(results)

    async def save(self, user: UserModel) -> UserModel:
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def email_exists(self, email: str) -> bool:
        result = await self.db.scalar(
            select(UserModel.id).where(UserModel.email == email)
        )
        return result is not None
