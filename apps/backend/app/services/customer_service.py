"""
Customer Service — business logic layer between API endpoints and repositories.
Encapsulates domain rules, triggers background tasks, and publishes events.
"""

import structlog
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import CustomerModel
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerOut
from app.workers.prediction_tasks import run_prediction_for_customer

logger = structlog.get_logger()


class CustomerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CustomerRepository(db)

    async def create(self, data: CustomerCreate, tenant_id: UUID) -> CustomerModel:
        """Create a new customer and queue initial predictions."""
        customer = CustomerModel(
            **data.model_dump(exclude_unset=True),
            tenant_id=tenant_id,
        )
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)

        # Queue ML predictions asynchronously
        run_prediction_for_customer.delay(
            customer_id=str(customer.id),
            tenant_id=str(tenant_id),
        )

        logger.info("Customer created", customer_id=str(customer.id),
                    tenant_id=str(tenant_id))
        return customer

    async def update(
        self, customer_id: UUID, data: CustomerUpdate, tenant_id: UUID
    ) -> CustomerModel:
        """Update customer fields and refresh predictions if scores changed."""
        customer = await self.repo.get_by_id(customer_id, tenant_id)
        if customer is None:
            raise ValueError(f"Customer {customer_id} not found")

        score_fields = {"health_score", "churn_probability", "lead_score"}
        updates = data.model_dump(exclude_unset=True)
        scores_changed = bool(score_fields & updates.keys())

        for field, value in updates.items():
            setattr(customer, field, value)

        await self.db.commit()
        await self.db.refresh(customer)

        if scores_changed:
            run_prediction_for_customer.delay(
                customer_id=str(customer.id),
                tenant_id=str(tenant_id),
            )

        return customer

    async def get_at_risk(self, tenant_id: UUID, threshold: float = 0.7):
        """Return all customers above the churn risk threshold."""
        return await self.repo.list_high_churn_risk(tenant_id, threshold)

    async def get_dashboard_stats(self, tenant_id: UUID) -> dict:
        """Aggregate stats for the analytics dashboard."""
        counts = await self.repo.count_by_status(tenant_id)
        total = sum(counts.values())
        return {
            "total_customers": total,
            "active_customers": counts.get("active", 0),
            "inactive_customers": counts.get("inactive", 0),
            "churned_customers": counts.get("churned", 0),
        }
