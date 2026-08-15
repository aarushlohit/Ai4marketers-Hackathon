"""Customer CRUD endpoints with pagination and filtering."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser, Pagination, get_current_user
from app.core.database import get_db
from app.models.customer import CustomerModel
from app.schemas.customer import CustomerCreate, CustomerListResponse, CustomerOut, CustomerUpdate

router = APIRouter()


@router.get("", response_model=CustomerListResponse)
async def list_customers(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
    pagination: Annotated[Pagination, Depends()],
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    crm_source: str | None = Query(default=None),
):
    """List customers with optional search, filter, and pagination."""
    q = select(CustomerModel).where(
        CustomerModel.tenant_id == user.tenant_id,
        CustomerModel.is_deleted.is_(False),
    )
    if search:
        like = f"%{search}%"
        q = q.where(
            (CustomerModel.first_name.ilike(like))
            | (CustomerModel.last_name.ilike(like))
            | (CustomerModel.email.ilike(like))
            | (CustomerModel.company.ilike(like))
        )
    if status:
        q = q.where(CustomerModel.status == status)
    if crm_source:
        q = q.where(CustomerModel.crm_source == crm_source)

    total = await db.scalar(select(func.count()).select_from(q.subquery()))
    results = await db.scalars(
        q.order_by(CustomerModel.created_at.desc())
         .offset(pagination.offset)
         .limit(pagination.page_size)
    )
    return CustomerListResponse(
        customers=list(results),
        total=total or 0,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Create a new customer record."""
    from app.api.v1.endpoints.billing import check_quota_limits
    await check_quota_limits(user.tenant_id, "customers", db)
    
    customer = CustomerModel(**payload.model_dump(), tenant_id=user.tenant_id)

    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer


@router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(
    customer_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Get a single customer by ID."""
    customer = await _get_or_404(db, customer_id, user.tenant_id)
    return customer


@router.put("/{customer_id}", response_model=CustomerOut)
async def update_customer(
    customer_id: UUID,
    payload: CustomerUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Update customer fields."""
    customer = await _get_or_404(db, customer_id, user.tenant_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    await db.commit()
    await db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Soft-delete a customer."""
    customer = await _get_or_404(db, customer_id, user.tenant_id)
    customer.is_deleted = True
    await db.commit()


async def _get_or_404(db: AsyncSession, customer_id: UUID, tenant_id: UUID) -> CustomerModel:
    customer = await db.scalar(
        select(CustomerModel).where(
            CustomerModel.id == customer_id,
            CustomerModel.tenant_id == tenant_id,
            CustomerModel.is_deleted.is_(False),
        )
    )
    if not customer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer
