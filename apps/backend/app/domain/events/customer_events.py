"""Domain events for customer lifecycle."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent:
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass(frozen=True)
class CustomerCreated(DomainEvent):
    customer_id: UUID = field(default_factory=uuid4)
    tenant_id: UUID = field(default_factory=uuid4)
    email: str = ""
    crm_source: str | None = None


@dataclass(frozen=True)
class CustomerUpdated(DomainEvent):
    customer_id: UUID = field(default_factory=uuid4)
    tenant_id: UUID = field(default_factory=uuid4)
    changed_fields: tuple = field(default_factory=tuple)


@dataclass(frozen=True)
class CustomerChurnRiskHigh(DomainEvent):
    """Raised when a customer's churn probability crosses 0.7."""
    customer_id: UUID = field(default_factory=uuid4)
    tenant_id: UUID = field(default_factory=uuid4)
    churn_probability: float = 0.0


@dataclass(frozen=True)
class CustomerDeleted(DomainEvent):
    customer_id: UUID = field(default_factory=uuid4)
    tenant_id: UUID = field(default_factory=uuid4)
    deleted_by: UUID | None = None
