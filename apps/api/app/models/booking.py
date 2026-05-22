import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings

from .base import Base


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = {"schema": settings.db_schema}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    booking_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    deal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{settings.db_schema}.deal_cards.id", ondelete="CASCADE"), nullable=False
    )
    practitioner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{settings.db_schema}.practitioners.id", ondelete="CASCADE"), nullable=False
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{settings.db_schema}.customers.id", ondelete="CASCADE"), nullable=False
    )

    customer_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    quantity: Mapped[int] = mapped_column(default=1, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fee_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="USD")

    payment_status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    redemption_status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")

    wallet_pass_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(f"{settings.db_schema}.wallet_passes.id", ondelete="SET NULL"), nullable=True
    )
    qr_code: Mapped[str | None] = mapped_column(String(500), nullable=True)

    booked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    redeemed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    deal = relationship("DealCard")
    practitioner = relationship("Practitioner")
    customer = relationship("Customer")
    wallet_pass = relationship("WalletPass", foreign_keys=[wallet_pass_id])
