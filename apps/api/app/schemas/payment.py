from pydantic import BaseModel, EmailStr
from typing import Literal
from uuid import UUID


class CheckoutSessionCreateRequest(BaseModel):
    deal_id: UUID
    customer_email: EmailStr
    customer_name: str | None = None
    quantity: int = 1
    success_url: str
    cancel_url: str


class CheckoutSessionCreateResponse(BaseModel):
    checkout_session_id: str
    checkout_url: str


class CheckoutSessionResultResponse(BaseModel):
    checkout_session_id: str
    status: Literal["pending", "ready"]
    wallet_pass_id: UUID | None = None
    booking_id: UUID | None = None
    booking_number: str | None = None
    qr_code: str | None = None
    apple_wallet_url: str | None = None
    google_wallet_url: str | None = None
    pass_url: str | None = None
