import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings

from .base import Base


class WalletPass(Base):
    __tablename__ = "wallet_passes"
    __table_args__ = {"schema": settings.db_schema}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    deal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{settings.db_schema}.deal_cards.id", ondelete="CASCADE"), nullable=False
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{settings.db_schema}.customers.id", ondelete="CASCADE"), nullable=False
    )
    qr_code: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    source_checkout_session_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    booking_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(f"{settings.db_schema}.bookings.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), default="issued", nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    redeemed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    wallet_type: Mapped[str] = mapped_column(String(32), default="apple", nullable=False)
    apple_wallet_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    google_wallet_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    deal = relationship("DealCard", back_populates="wallet_passes")
    customer = relationship("Customer", back_populates="wallet_passes")

    @property
    def owner_id(self) -> uuid.UUID:
        return self.customer_id

    @property
    def wallet_provider(self) -> str:
        return (self.wallet_type or "internal").strip().lower()

    @property
    def pass_status(self) -> str:
        return self.status

    @property
    def redemption_status(self) -> str:
        if self.status == "redeemed":
            return "redeemed"
        if self.status in {"expired", "revoked"}:
            return self.status
        return "active"
