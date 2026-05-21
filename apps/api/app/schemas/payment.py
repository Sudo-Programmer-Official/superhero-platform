from pydantic import BaseModel, EmailStr
from uuid import UUID


class CheckoutSessionCreateRequest(BaseModel):
    deal_id: UUID
    customer_email: EmailStr
    customer_name: str | None = None
    success_url: str
    cancel_url: str


class CheckoutSessionCreateResponse(BaseModel):
    checkout_session_id: str
    checkout_url: str
