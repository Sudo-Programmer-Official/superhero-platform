from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WalletPassIssueRequest(BaseModel):
    deal_id: UUID
    customer_id: UUID
    wallet_type: str = "apple"


class WalletPassRedeemRequest(BaseModel):
    qr_code: str


class WalletPassExpireRequest(BaseModel):
    reason: str | None = None


class WalletPassRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    deal_id: UUID
    customer_id: UUID
    qr_code: str
    status: str
    redeemed_at: datetime | None
    wallet_type: str
    created_at: datetime
