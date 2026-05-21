from pydantic import BaseModel


class StripeConnectStartRequest(BaseModel):
    refresh_url: str
    return_url: str


class StripeConnectStartResponse(BaseModel):
    onboarding_url: str
    account_id: str


class StripeConnectStatusResponse(BaseModel):
    account_id: str | None
    onboarding_complete: bool
    payouts_enabled: bool
    charges_enabled: bool
