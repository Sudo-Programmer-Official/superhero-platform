"""add activity events pipeline table

Revision ID: 20260522_0007
Revises: 20260522_0006
Create Date: 2026-05-22
"""

from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260522_0007"
down_revision: Union[str, Sequence[str], None] = "20260522_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "superhero_platform")


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_tables = set(inspector.get_table_names(schema=SCHEMA))
    if "activity_events" not in existing_tables:
        op.create_table(
            "activity_events",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("actor_id", sa.String(length=128), nullable=True),
            sa.Column("entity_type", sa.String(length=64), nullable=False),
            sa.Column("entity_id", sa.String(length=128), nullable=False),
            sa.Column("event_type", sa.String(length=128), nullable=False),
            sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.PrimaryKeyConstraint("id"),
            schema=SCHEMA,
        )

    existing_indexes = {idx["name"] for idx in inspector.get_indexes("activity_events", schema=SCHEMA)}
    if "ix_activity_events_event_type" not in existing_indexes:
        op.create_index("ix_activity_events_event_type", "activity_events", ["event_type"], schema=SCHEMA)
    if "ix_activity_events_entity" not in existing_indexes:
        op.create_index("ix_activity_events_entity", "activity_events", ["entity_type", "entity_id"], schema=SCHEMA)
    if "ix_activity_events_created_at" not in existing_indexes:
        op.create_index("ix_activity_events_created_at", "activity_events", ["created_at"], schema=SCHEMA)


def downgrade() -> None:
    op.drop_index("ix_activity_events_created_at", table_name="activity_events", schema=SCHEMA)
    op.drop_index("ix_activity_events_entity", table_name="activity_events", schema=SCHEMA)
    op.drop_index("ix_activity_events_event_type", table_name="activity_events", schema=SCHEMA)
    op.drop_table("activity_events", schema=SCHEMA)
