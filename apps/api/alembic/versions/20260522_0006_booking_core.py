"""add bookings transactional core

Revision ID: 20260522_0006
Revises: 20260522_0005
Create Date: 2026-05-22
"""

from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260522_0006"
down_revision: Union[str, Sequence[str], None] = "20260522_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = os.getenv("DB_SCHEMA", "superhero_platform")


def upgrade() -> None:
    op.create_table(
        "bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("booking_number", sa.String(length=64), nullable=False),
        sa.Column("deal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("practitioner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_name", sa.String(length=160), nullable=True),
        sa.Column("customer_email", sa.String(length=255), nullable=False),
        sa.Column("customer_phone", sa.String(length=64), nullable=True),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=False),
        sa.Column("fee_amount", sa.Numeric(10, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default=sa.text("'USD'")),
        sa.Column("payment_status", sa.String(length=32), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("redemption_status", sa.String(length=32), nullable=False, server_default=sa.text("'active'")),
        sa.Column("wallet_pass_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("qr_code", sa.String(length=500), nullable=True),
        sa.Column("booked_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("redeemed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refunded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["deal_id"], [f"{SCHEMA}.deal_cards.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["practitioner_id"], [f"{SCHEMA}.practitioners.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["customer_id"], [f"{SCHEMA}.customers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["wallet_pass_id"], [f"{SCHEMA}.wallet_passes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("booking_number", name="uq_bookings_booking_number"),
        schema=SCHEMA,
    )

    op.add_column(
        "wallet_passes",
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), nullable=True),
        schema=SCHEMA,
    )
    op.create_foreign_key(
        "fk_wallet_passes_booking_id",
        "wallet_passes",
        "bookings",
        ["booking_id"],
        ["id"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_wallet_passes_booking_id", "wallet_passes", schema=SCHEMA, type_="foreignkey")
    op.drop_column("wallet_passes", "booking_id", schema=SCHEMA)
    op.drop_table("bookings", schema=SCHEMA)
