"""Pydantic schemas for customer requests and responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class CustomerCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    company: str | None = Field(default=None, max_length=255)
    title: str | None = Field(default=None, max_length=100)


class CustomerUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = None
    company: str | None = None
    title: str | None = None
    status: str | None = None


class CustomerOut(BaseModel):
    id: UUID
    tenant_id: UUID
    external_id: str | None
    crm_source: str | None
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    company: str | None
    title: str | None
    status: str
    health_score: float | None
    churn_probability: float | None
    lead_score: int | None
    lifetime_value: float | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerListResponse(BaseModel):
    customers: list[CustomerOut]
    total: int
    page: int
    page_size: int
