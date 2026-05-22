from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator


class DealCardCreate(BaseModel):
    practitioner_id: UUID
    title: str
    cta_text: str | None = None
    booking_url: str | None = None
    description: str | None = None
    image: str | None = None
    price: Decimal
    capacity: int
    location: str
    timezone: str = "UTC"
    start_time: datetime
    end_time: datetime
    expiration_time: datetime | None = None
    share_link: str | None = None
    wallet_enabled: bool = True


class DealCardUpdate(BaseModel):
    title: str | None = None
    cta_text: str | None = None
    booking_url: str | None = None
    description: str | None = None
    image: str | None = None
    price: Decimal | None = None
    capacity: int | None = None
    remaining_slots: int | None = None
    location: str | None = None
    timezone: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    expiration_time: datetime | None = None
    share_link: str | None = None
    status: str | None = None  # draft | published | expired | canceled
    wallet_enabled: bool | None = None


class DealCardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    practitioner_id: UUID
    title: str
    slug: str
    cta_text: str | None
    booking_url: str | None
    description: str | None
    image: str | None
    price: Decimal
    capacity: int
    remaining_slots: int
    location: str
    start_time: datetime
    end_time: datetime
    expiration_time: datetime | None
    share_link: str | None
    status: str
    wallet_enabled: bool
    created_at: datetime
    updated_at: datetime

    # Canonical Deal Domain Fields
    owner_id: UUID | None = None
    organization_id: UUID | None = None
    subtitle: str | None = None
    category: str | None = None
    cover_image: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    timezone: str = "UTC"
    location_name: str | None = None
    location_address: str | None = None
    total_seats: int | None = None
    seats_remaining: int | None = None
    sold_count: int = 0
    currency: str = "USD"
    base_price: Decimal | None = None
    fee_amount: Decimal = Decimal("0.00")
    total_price: Decimal | None = None
    redemption_type: str = "qr"
    public_url: str | None = None
    qr_code_url: str | None = None
    views: int = 0
    conversions: int = 0
    revenue: Decimal = Decimal("0.00")
    published_at: datetime | None = None

    @model_validator(mode="after")
    def populate_canonical_fields(self) -> "DealCardRead":
        self.owner_id = self.practitioner_id
        self.subtitle = self.cta_text
        self.cover_image = self.image
        self.start_at = self.start_time
        self.end_at = self.end_time
        self.location_name = self.location
        self.total_seats = self.capacity
        self.seats_remaining = self.remaining_slots
        self.sold_count = max(0, self.capacity - self.remaining_slots)
        self.base_price = self.price
        self.total_price = (self.base_price or Decimal("0.00")) + self.fee_amount
        self.public_url = self.share_link
        self.conversions = self.sold_count
        self.revenue = (self.base_price or Decimal("0.00")) * Decimal(self.sold_count)
        if self.status == "canceled":
            self.status = "archived"
        if self.status == "published":
            self.published_at = self.updated_at
        return self
