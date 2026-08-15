"""
Customer domain entity — pure business logic, no I/O.
Follows DDD: encapsulates invariants and behaviour.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class CustomerEntity:
    """
    The Customer aggregate root in the domain layer.
    All business rules about a customer live here.
    """

    id: UUID = field(default_factory=uuid4)
    tenant_id: UUID = field(default_factory=uuid4)
    first_name: str = ""
    last_name: str = ""
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    title: str | None = None
    status: str = "active"
    external_id: str | None = None
    crm_source: str | None = None

    # AI/ML cached scores
    health_score: float | None = None
    churn_probability: float | None = None
    lead_score: int | None = None
    lifetime_value: float | None = None

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    is_deleted: bool = False

    # ── Business rules ────────────────────────────────────────

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def churn_risk_level(self) -> str:
        """Classify churn risk from probability."""
        if self.churn_probability is None:
            return "unknown"
        if self.churn_probability >= 0.7:
            return "high"
        if self.churn_probability >= 0.4:
            return "medium"
        return "low"

    @property
    def lead_grade(self) -> str:
        """Convert numeric lead score to letter grade."""
        if self.lead_score is None:
            return "–"
        if self.lead_score >= 80:
            return "A"
        if self.lead_score >= 65:
            return "B"
        if self.lead_score >= 50:
            return "C"
        if self.lead_score >= 35:
            return "D"
        return "F"

    def deactivate(self) -> None:
        """Mark customer as inactive."""
        self.status = "inactive"
        self.updated_at = datetime.now(timezone.utc)

    def mark_churned(self) -> None:
        """Mark customer as churned."""
        self.status = "churned"
        self.updated_at = datetime.now(timezone.utc)

    def soft_delete(self) -> None:
        """Soft-delete: hide from queries but retain for audit."""
        self.is_deleted = True
        self.updated_at = datetime.now(timezone.utc)

    def update_scores(
        self,
        health_score: float | None = None,
        churn_probability: float | None = None,
        lead_score: int | None = None,
        lifetime_value: float | None = None,
    ) -> None:
        """Update AI/ML prediction scores."""
        if health_score is not None:
            self.health_score = max(0.0, min(100.0, health_score))
        if churn_probability is not None:
            self.churn_probability = max(0.0, min(1.0, churn_probability))
        if lead_score is not None:
            self.lead_score = max(0, min(100, lead_score))
        if lifetime_value is not None:
            self.lifetime_value = max(0.0, lifetime_value)
        self.updated_at = datetime.now(timezone.utc)

    def is_at_risk(self) -> bool:
        return self.churn_risk_level in ("high", "medium")
