"""add practitioner stripe fields

Revision ID: 20260521_0002
Revises: 20260520_0001
Create Date: 2026-05-21
"""

from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260521_0002"
down_revision: Union[str, Sequence[str], None] = "20260520_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "superhero_platform")


def upgrade() -> None:
    op.add_column(
        "practitioners",
        sa.Column("stripe_account_id", sa.String(length=64), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "practitioners",
        sa.Column("stripe_onboarding_complete", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        schema=SCHEMA,
    )
    op.create_unique_constraint(
        "uq_practitioners_stripe_account_id",
        "practitioners",
        ["stripe_account_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_constraint("uq_practitioners_stripe_account_id", "practitioners", schema=SCHEMA, type_="unique")
    op.drop_column("practitioners", "stripe_onboarding_complete", schema=SCHEMA)
    op.drop_column("practitioners", "stripe_account_id", schema=SCHEMA)
