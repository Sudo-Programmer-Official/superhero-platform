import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings

from .base import Base


class Practitioner(Base):
    __tablename__ = "practitioners"
    __table_args__ = {"schema": settings.db_schema}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    social_links: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    branding: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    firebase_uid: Mapped[str | None] = mapped_column(String(128), unique=True, nullable=True)
    stripe_account_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    stripe_onboarding_complete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    deals = relationship("DealCard", back_populates="practitioner", cascade="all, delete-orphan")

    @property
    def avatar_url(self) -> str | None:
        return self.profile_image

    @property
    def cover_image_url(self) -> str | None:
        return (self.branding or {}).get("cover_image_url")

    @property
    def logo_url(self) -> str | None:
        return (self.branding or {}).get("logo_url")

    @property
    def category(self) -> str | None:
        return (self.branding or {}).get("category")

    @property
    def tagline(self) -> str | None:
        return (self.branding or {}).get("tagline")

    @property
    def specialties(self) -> list[str]:
        raw = (self.branding or {}).get("specialties")
        return raw if isinstance(raw, list) else []

    @property
    def booking_policies(self) -> str | None:
        return (self.branding or {}).get("booking_policies")

    @property
    def website(self) -> str | None:
        return (self.social_links or {}).get("website")

    @property
    def support_email(self) -> str | None:
        return (self.branding or {}).get("support_email")

    @property
    def accent_color(self) -> str | None:
        return (self.branding or {}).get("accent_color")

    @property
    def verification_state(self) -> str:
        return (self.branding or {}).get("verification_state") or "unverified"
