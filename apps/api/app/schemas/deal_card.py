from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DealCardCreate(BaseModel):
    practitioner_id: UUID
    title: str
    description: str | None = None
    image: str | None = None
    price: Decimal
    capacity: int
    location: str
    start_time: datetime
    end_time: datetime
    expiration_time: datetime | None = None
    share_link: str | None = None
    wallet_enabled: bool = True


class DealCardUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    image: str | None = None
    price: Decimal | None = None
    capacity: int | None = None
    remaining_slots: int | None = None
    location: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    expiration_time: datetime | None = None
    share_link: str | None = None
    wallet_enabled: bool | None = None


class DealCardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    practitioner_id: UUID
    title: str
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
    wallet_enabled: bool
    created_at: datetime
