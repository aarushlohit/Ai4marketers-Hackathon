"""
Customer Repository — data access layer.
Abstracts all SQLAlchemy queries behind a clean interface
so the domain and use-case layers stay free of DB concerns.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import CustomerModel


class CustomerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, customer_id: UUID, tenant_id: UUID) -> CustomerModel | None:
        return await self.db.scalar(
            select(CustomerModel).where(
                CustomerModel.id == customer_id,
                CustomerModel.tenant_id == tenant_id,
                CustomerModel.is_deleted.is_(False),
            )
        )

    async def get_by_external_id(
        self, external_id: str, crm_source: str, tenant_id: UUID
    ) -> CustomerModel | None:
        return await self.db.scalar(
            select(CustomerModel).where(
                CustomerModel.external_id == external_id,
                CustomerModel.crm_source == crm_source,
                CustomerModel.tenant_id == tenant_id,
            )
        )

    async def list_paginated(
        self,
        tenant_id: UUID,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        status: str | None = None,
        crm_source: str | None = None,
    ) -> tuple[list[CustomerModel], int]:
        q = select(CustomerModel).where(
            CustomerModel.tenant_id == tenant_id,
            CustomerModel.is_deleted.is_(False),
        )
        if search:
            like = f"%{search}%"
            q = q.where(
                CustomerModel.first_name.ilike(like)
                | CustomerModel.last_name.ilike(like)
                | CustomerModel.email.ilike(like)
                | CustomerModel.company.ilike(like)
            )
        if status:
            q = q.where(CustomerModel.status == status)
        if crm_source:
            q = q.where(CustomerModel.crm_source == crm_source)

        total = await self.db.scalar(
            select(func.count()).select_from(q.subquery())
        )
        offset = (page - 1) * page_size
        results = await self.db.scalars(
            q.order_by(CustomerModel.created_at.desc())
             .offset(offset)
             .limit(page_size)
        )
        return list(results), (total or 0)

    async def save(self, customer: CustomerModel) -> CustomerModel:
        self.db.add(customer)
        await self.db.flush()
        await self.db.refresh(customer)
        return customer

    async def upsert_from_crm(
        self, external_id: str, crm_source: str, tenant_id: UUID, data: dict
    ) -> CustomerModel:
        """Create or update a customer record from a CRM sync."""
        existing = await self.get_by_external_id(external_id, crm_source, tenant_id)
        if existing:
            for k, v in data.items():
                if hasattr(existing, k) and v is not None:
                    setattr(existing, k, v)
            return await self.save(existing)
        customer = CustomerModel(
            external_id=external_id,
            crm_source=crm_source,
            tenant_id=tenant_id,
            **{k: v for k, v in data.items() if hasattr(CustomerModel, k)},
        )
        return await self.save(customer)

    async def list_high_churn_risk(
        self, tenant_id: UUID, threshold: float = 0.7
    ) -> list[CustomerModel]:
        results = await self.db.scalars(
            select(CustomerModel).where(
                CustomerModel.tenant_id == tenant_id,
                CustomerModel.churn_probability >= threshold,
                CustomerModel.is_deleted.is_(False),
            ).order_by(CustomerModel.churn_probability.desc())
        )
        return list(results)

    async def count_by_status(self, tenant_id: UUID) -> dict[str, int]:
        rows = await self.db.execute(
            select(CustomerModel.status, func.count())
            .where(CustomerModel.tenant_id == tenant_id,
                   CustomerModel.is_deleted.is_(False))
            .group_by(CustomerModel.status)
        )
        return {row[0]: row[1] for row in rows}
