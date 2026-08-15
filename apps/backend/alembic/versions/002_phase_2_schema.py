"""Phase 2 schema changes.

Revision ID: 002_phase_2_schema
Revises: 001_initial_schema
Create Date: 2026-07-15 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "002_phase_2_schema"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. workflows.workflows
    op.create_table(
        "workflows",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1000)),
        sa.Column("conditions", JSONB(), nullable=False, server_default="{}"),
        sa.Column("actions", JSONB(), nullable=False, server_default="[]"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        schema="workflows",
    )
    op.create_index("ix_workflows_tenant_status", "workflows", ["tenant_id", "is_active"], schema="workflows")

    # 2. ai.recommendations
    op.create_table(
        "recommendations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", UUID(as_uuid=True), sa.ForeignKey("customers.customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(100), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("expected_revenue", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("status", sa.String(50), nullable=False, server_default="Pending"),
        sa.Column("business_reason", sa.Text()),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        schema="ai",
    )
    op.create_index("ix_recommendations_tenant_customer", "recommendations", ["tenant_id", "customer_id"], schema="ai")

    # 3. ai.feedback_logs
    op.create_table(
        "feedback_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("recommendation_id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("core.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feedback_text", sa.Text()),
        sa.Column("rating", sa.Integer()),
        sa.Column("outcome_achieved", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        schema="ai",
    )
    op.create_index("ix_feedback_tenant_recommendation", "feedback_logs", ["tenant_id", "recommendation_id"], schema="ai")

    # 4. ai.meeting_summaries
    op.create_table(
        "meeting_summaries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", UUID(as_uuid=True), sa.ForeignKey("customers.customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("transcript_summary", sa.Text()),
        sa.Column("action_items", JSONB(), nullable=False, server_default="[]"),
        sa.Column("sentiment", sa.String(50)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        schema="ai",
    )
    op.create_index("ix_meetings_tenant_customer", "meeting_summaries", ["tenant_id", "customer_id"], schema="ai")


def downgrade() -> None:
    op.drop_table("meeting_summaries", schema="ai")
    op.drop_table("feedback_logs", schema="ai")
    op.drop_table("recommendations", schema="ai")
    op.drop_table("workflows", schema="workflows")
