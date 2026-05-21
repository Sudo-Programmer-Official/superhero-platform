from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PractitionerCreate(BaseModel):
    name: str
    bio: str | None = None
    profile_image: str | None = None
    location: str | None = None


class PractitionerUpdate(BaseModel):
    name: str | None = None
    bio: str | None = None
    profile_image: str | None = None
    location: str | None = None


class PractitionerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    bio: str | None
    profile_image: str | None
    location: str | None
    firebase_uid: str | None
    created_at: datetime
