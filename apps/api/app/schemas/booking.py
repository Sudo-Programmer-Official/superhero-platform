from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    booking_number: str
    deal_id: UUID
    practitioner_id: UUID
    customer_id: UUID

    customer_name: str | None
    customer_email: str
    customer_phone: str | None
    avatar_url: str | None

    quantity: int
    subtotal: Decimal
    fee_amount: Decimal
    total_amount: Decimal
    currency: str

    payment_status: str
    redemption_status: str

    wallet_pass_id: UUID | None
    qr_code: str | None

    booked_at: datetime
    redeemed_at: datetime | None
    refunded_at: datetime | None

    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def normalize_status(self) -> "BookingRead":
        if self.payment_status not in {"pending", "paid", "refunded", "failed"}:
            self.payment_status = "pending"
        if self.redemption_status not in {"active", "redeemed", "expired"}:
            self.redemption_status = "active"
        return self
