"""
Use Case: Register User
Creates a new tenant + admin user in a single transaction.
"""

import structlog
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.domain.value_objects.email import Email
from app.models.user import UserModel
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest

logger = structlog.get_logger()


class RegisterUserUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def execute(self, request: RegisterRequest) -> UserModel:
        """
        Register a new user.
        - Validates email format via value object
        - Checks for duplicate email
        - Creates user with hashed password
        - First user in a new signup gets 'admin' role
        """
        # Validate email
        try:
            email_vo = Email(request.email)
        except ValueError as e:
            raise ValueError(str(e))

        # Check uniqueness
        if await self.user_repo.email_exists(request.email):
            raise ValueError(f"Email {request.email} is already registered")

        # Every sign-up creates its own tenant (multi-tenant SaaS)
        tenant_id = uuid4()

        user = UserModel(
            tenant_id=tenant_id,
            email=request.email,
            hashed_password=hash_password(request.password),
            first_name=request.first_name,
            last_name=request.last_name,
            role="admin",  # founder/first user is admin
        )
        await self.user_repo.save(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info("User registered", user_id=str(user.id), tenant_id=str(tenant_id))
        return user
