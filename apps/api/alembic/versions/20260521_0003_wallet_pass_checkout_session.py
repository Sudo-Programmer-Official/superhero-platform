"""add wallet pass checkout session id

Revision ID: 20260521_0003
Revises: 20260521_0002
Create Date: 2026-05-21
"""

from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260521_0003"
down_revision: Union[str, Sequence[str], None] = "20260521_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "superhero_platform")


def upgrade() -> None:
    op.add_column(
        "wallet_passes",
        sa.Column("source_checkout_session_id", sa.String(length=255), nullable=True),
        schema=SCHEMA,
    )
    op.create_unique_constraint(
        "uq_wallet_passes_source_checkout_session_id",
        "wallet_passes",
        ["source_checkout_session_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_wallet_passes_source_checkout_session_id",
        "wallet_passes",
        schema=SCHEMA,
        type_="unique",
    )
    op.drop_column("wallet_passes", "source_checkout_session_id", schema=SCHEMA)
