"""add activity event scope columns

Revision ID: 20260522_0008
Revises: 20260522_0007
Create Date: 2026-05-22
"""

from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa


revision: str = "20260522_0008"
down_revision: Union[str, Sequence[str], None] = "20260522_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "superhero_platform")


def upgrade() -> None:
    op.add_column(
        "activity_events",
        sa.Column("tenant_id", sa.String(length=64), nullable=False, server_default=sa.text("'default'")),
        schema=SCHEMA,
    )
    op.add_column(
        "activity_events",
        sa.Column("practitioner_id", sa.String(length=128), nullable=True),
        schema=SCHEMA,
    )
    op.create_index("ix_activity_events_tenant_id", "activity_events", ["tenant_id"], schema=SCHEMA)
    op.create_index(
        "ix_activity_events_tenant_practitioner_created",
        "activity_events",
        ["tenant_id", "practitioner_id", "created_at"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index("ix_activity_events_tenant_practitioner_created", table_name="activity_events", schema=SCHEMA)
    op.drop_index("ix_activity_events_tenant_id", table_name="activity_events", schema=SCHEMA)
    op.drop_column("activity_events", "practitioner_id", schema=SCHEMA)
    op.drop_column("activity_events", "tenant_id", schema=SCHEMA)
