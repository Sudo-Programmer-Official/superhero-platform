from datetime import datetime
from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class WalletPassIssueRequest(BaseModel):
    deal_id: UUID
    customer_id: UUID
    wallet_type: str = "apple"


class WalletPassRedeemRequest(BaseModel):
    qr_code: str


class WalletPassExpireRequest(BaseModel):
    reason: str | None = None


class WalletPassRestoreRequest(BaseModel):
    reason: str | None = None


class WalletPassRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    booking_id: UUID | None
    deal_id: UUID
    owner_id: UUID = Field(validation_alias=AliasChoices("owner_id", "customer_id"))
    customer_id: UUID
    qr_code: str
    pass_status: str = Field(validation_alias=AliasChoices("pass_status", "status"))
    redemption_status: str = "active"
    expires_at: datetime | None
    redeemed_at: datetime | None
    source_checkout_session_id: str | None
    wallet_provider: str = Field(validation_alias=AliasChoices("wallet_provider", "wallet_type"))
    wallet_type: str
    apple_wallet_url: str | None
    google_wallet_url: str | None
    created_at: datetime
