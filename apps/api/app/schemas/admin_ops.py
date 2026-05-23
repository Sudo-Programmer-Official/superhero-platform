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
