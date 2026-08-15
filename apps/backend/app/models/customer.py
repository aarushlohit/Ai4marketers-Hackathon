"""SQLAlchemy ORM model for customers."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CustomerModel(Base):
    __tablename__ = "customers"
    __table_args__ = (
        Index("ix_customers_tenant_email", "tenant_id", "email"),
        Index("ix_customers_tenant_status", "tenant_id", "status"),
        {"schema": "customers"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    crm_source: Mapped[str | None] = mapped_column(String(50), nullable=True)

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", index=True)

    # AI-computed fields (cached from ML engine)
    health_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    churn_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    lead_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lifetime_value: Mapped[float | None] = mapped_column(Float, nullable=True)

    attributes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Customer {self.first_name} {self.last_name}>"
