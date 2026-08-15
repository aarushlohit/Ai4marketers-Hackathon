"""Add customer unique index.

Revision ID: 003_add_customer_unique_index
Revises: 002_phase_2_schema
Create Date: 2026-08-15 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003_add_customer_unique_index"
down_revision: Union[str, None] = "002_phase_2_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "uq_customers_tenant_external_source",
        "customers",
        ["tenant_id", "external_id", "crm_source"],
        unique=True,
        schema="customers",
        postgresql_where=sa.text("external_id IS NOT NULL")
    )


def downgrade() -> None:
    op.drop_index(
        "uq_customers_tenant_external_source",
        table_name="customers",
        schema="customers"
    )
