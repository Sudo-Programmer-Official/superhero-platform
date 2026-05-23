"""add wallet pass operational fields

Revision ID: 20260523_0009
Revises: 20260522_0008
Create Date: 2026-05-23
"""

from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa

revision: str = "20260523_0009"
down_revision: Union[str, Sequence[str], None] = "20260522_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "superhero_platform")


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    columns = {column["name"] for column in inspector.get_columns("wallet_passes", schema=SCHEMA)}

    if "expires_at" not in columns:
        op.add_column("wallet_passes", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True), schema=SCHEMA)
    if "apple_wallet_url" not in columns:
        op.add_column("wallet_passes", sa.Column("apple_wallet_url", sa.String(length=500), nullable=True), schema=SCHEMA)
    if "google_wallet_url" not in columns:
        op.add_column("wallet_passes", sa.Column("google_wallet_url", sa.String(length=500), nullable=True), schema=SCHEMA)


def downgrade() -> None:
    op.drop_column("wallet_passes", "google_wallet_url", schema=SCHEMA)
    op.drop_column("wallet_passes", "apple_wallet_url", schema=SCHEMA)
    op.drop_column("wallet_passes", "expires_at", schema=SCHEMA)
