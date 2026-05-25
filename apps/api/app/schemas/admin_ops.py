from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class AdminPractitionerRow(BaseModel):
    id: UUID
    name: str
    slug: str
    subscription_status: str
    payout_status: str
    stripe_state: str
    verification_state: str
    health: str
    is_public: bool
    created_at: datetime


class AdminPractitionerActionRequest(BaseModel):
    action: str


class AdminDealRow(BaseModel):
    id: UUID
    title: str
    slug: str
    practitioner_id: UUID
    practitioner_name: str
    status: str
    moderation_state: str
    revenue: Decimal
    bookings_count: int
    start_time: datetime
    created_at: datetime


class AdminDealActionRequest(BaseModel):
    action: str


class AdminPayoutRow(BaseModel):
    id: str
    practitioner_id: UUID
    creator: str
    amount: Decimal
    status: str
    transfer_state: str
    transaction_count: int
    processing_date: datetime | None = None
    payout_date: datetime | None = None


class AdminPayoutActionRequest(BaseModel):
    action: str


class AdminBookingRow(BaseModel):
    id: UUID
    booking_number: str
    deal_title: str
    practitioner_name: str
    customer_name: str | None
    customer_email: str
    quantity: int
    total_amount: Decimal
    currency: str
    payment_status: str
    redemption_status: str
    wallet_pass_id: UUID | None
    created_at: datetime


class AdminWalletPassRow(BaseModel):
    id: UUID
    deal_title: str
    practitioner_name: str
    attendee_email: str | None
    booking_number: str | None
    pass_status: str
    redemption_status: str
    wallet_type: str
    source_checkout_session_id: str | None
    qr_code: str
    created_at: datetime


class AdminRedemptionRow(BaseModel):
    wallet_pass_id: str
    deal_title: str | None
    practitioner_name: str | None
    attendee_email: str | None
    success_count: int
    failed_count: int
    duplicate_attempts: int
    invalid_attempts: int
    last_event_at: datetime
    risk_level: str


class AdminTimelineEventRow(BaseModel):
    id: UUID
    entity_type: str
    entity_id: str
    event_type: str
    metadata: dict
    created_at: datetime
