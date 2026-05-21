import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings

from .base import Base


class DealCard(Base):
    __tablename__ = "deal_cards"
    __table_args__ = {"schema": settings.db_schema}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    practitioner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{settings.db_schema}.practitioners.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_slots: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expiration_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    share_link: Mapped[str | None] = mapped_column(String(500), unique=True, nullable=True)
    cta_text: Mapped[str | None] = mapped_column(String(120), nullable=True)
    booking_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    wallet_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    practitioner = relationship("Practitioner", back_populates="deals")
    wallet_passes = relationship("WalletPass", back_populates="deal", cascade="all, delete-orphan")
