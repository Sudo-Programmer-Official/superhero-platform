"""mvp lifecycle, public visibility, and slugs

Revision ID: 20260521_0004
Revises: 20260521_0003
Create Date: 2026-05-21
"""

from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260521_0004"
down_revision: Union[str, Sequence[str], None] = "20260521_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "superhero_platform")


def upgrade() -> None:
    op.add_column("practitioners", sa.Column("slug", sa.String(length=180), nullable=True), schema=SCHEMA)
    op.add_column(
        "practitioners",
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        schema=SCHEMA,
    )

    op.add_column("deal_cards", sa.Column("slug", sa.String(length=220), nullable=True), schema=SCHEMA)
    op.add_column("deal_cards", sa.Column("cta_text", sa.String(length=120), nullable=True), schema=SCHEMA)
    op.add_column("deal_cards", sa.Column("booking_url", sa.String(length=500), nullable=True), schema=SCHEMA)
    op.add_column(
        "deal_cards",
        sa.Column("status", sa.String(length=32), nullable=False, server_default=sa.text("'draft'")),
        schema=SCHEMA,
    )

    op.execute(sa.text(f"UPDATE {SCHEMA}.practitioners SET slug = CONCAT('practitioner-', SUBSTRING(id::text, 1, 8)) WHERE slug IS NULL"))
    op.execute(sa.text(f"UPDATE {SCHEMA}.deal_cards SET slug = CONCAT('deal-', SUBSTRING(id::text, 1, 8)) WHERE slug IS NULL"))

    op.alter_column("practitioners", "slug", nullable=False, schema=SCHEMA)
    op.alter_column("deal_cards", "slug", nullable=False, schema=SCHEMA)

    op.create_unique_constraint("uq_practitioners_slug", "practitioners", ["slug"], schema=SCHEMA)
    op.create_unique_constraint("uq_deal_cards_slug", "deal_cards", ["slug"], schema=SCHEMA)


def downgrade() -> None:
    op.drop_constraint("uq_deal_cards_slug", "deal_cards", schema=SCHEMA, type_="unique")
    op.drop_constraint("uq_practitioners_slug", "practitioners", schema=SCHEMA, type_="unique")

    op.drop_column("deal_cards", "status", schema=SCHEMA)
    op.drop_column("deal_cards", "booking_url", schema=SCHEMA)
    op.drop_column("deal_cards", "cta_text", schema=SCHEMA)
    op.drop_column("deal_cards", "slug", schema=SCHEMA)

    op.drop_column("practitioners", "is_public", schema=SCHEMA)
    op.drop_column("practitioners", "slug", schema=SCHEMA)
