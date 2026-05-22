"""add timezone to deal cards

Revision ID: 20260522_0005
Revises: 20260521_0004
Create Date: 2026-05-22
"""

from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa


revision: str = "20260522_0005"
down_revision: Union[str, Sequence[str], None] = "20260521_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "superhero_platform")


def upgrade() -> None:
    op.add_column(
        "deal_cards",
        sa.Column("timezone", sa.String(length=64), nullable=False, server_default=sa.text("'UTC'")),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("deal_cards", "timezone", schema=SCHEMA)
