"""Initial schema — creates all core tables.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-07-13 00:00:00.000000

NOTE: For a fresh database, prefer running init.sql directly via Docker.
This migration is for incremental changes after initial setup.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable extensions (idempotent)
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    # Create schemas
    for schema in ("core", "customers", "predictions", "integrations",
                   "ai", "workflows", "analytics", "security"):
        op.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

    # core.tenants
    op.create_table(
        "tenants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("plan", sa.String(50), nullable=False, server_default="standard"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("settings", JSONB(), server_default="{}"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True),
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True),
                  server_default=sa.func.now()),
        schema="core",
    )

    # core.users
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("tenant_id", UUID(as_uuid=True),
                  sa.ForeignKey("core.tenants.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="user"),
        sa.Column("phone", sa.String(50)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("last_login", sa.TIMESTAMP(timezone=True)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True),
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True),
                  server_default=sa.func.now()),
        schema="core",
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"], schema="core")
    op.create_index("ix_users_email", "users", ["email"], schema="core")

    # customers.customers
    op.create_table(
        "customers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.String(255)),
        sa.Column("crm_source", sa.String(50)),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255)),
        sa.Column("phone", sa.String(50)),
        sa.Column("company", sa.String(255)),
        sa.Column("title", sa.String(100)),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("health_score", sa.Float()),
        sa.Column("churn_probability", sa.Float()),
        sa.Column("lead_score", sa.Integer()),
        sa.Column("lifetime_value", sa.Float()),
        sa.Column("attributes", JSONB(), server_default="{}"),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True),
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True),
                  server_default=sa.func.now()),
        schema="customers",
    )
    op.create_index("ix_customers_tenant_status", "customers",
                    ["tenant_id", "status"], schema="customers")
    op.create_index("ix_customers_tenant_email", "customers",
                    ["tenant_id", "email"], schema="customers")

    # integrations.crm_connections
    op.create_table(
        "crm_connections",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("crm_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("access_token", sa.Text()),
        sa.Column("refresh_token", sa.Text()),
        sa.Column("token_expires_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("instance_url", sa.Text()),
        sa.Column("last_sync_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("sync_config", JSONB(), server_default="{}"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True),
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True),
                  server_default=sa.func.now()),
        schema="integrations",
    )
    op.create_unique_constraint(
        "uq_connections_tenant_crm", "crm_connections",
        ["tenant_id", "crm_type"], schema="integrations",
    )


def downgrade() -> None:
    op.drop_table("crm_connections", schema="integrations")
    op.drop_table("customers", schema="customers")
    op.drop_table("users", schema="core")
    op.drop_table("tenants", schema="core")
