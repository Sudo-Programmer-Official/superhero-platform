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
    slug: str | None = None
    avatar_url: str | None = None
    cover_image_url: str | None = None
    logo_url: str | None = None
    bio: str | None = None
    profile_image: str | None = None
    category: str | None = None
    tagline: str | None = None
    specialties: list[str] | None = None
    booking_policies: str | None = None
    website: str | None = None
    support_email: str | None = None
    accent_color: str | None = None
    verification_state: str | None = None
    social_links: dict | None = None
    location: str | None = None


class PractitionerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    avatar_url: str | None
    cover_image_url: str | None
    logo_url: str | None
    bio: str | None
    profile_image: str | None
    category: str | None
    tagline: str | None
    specialties: list[str]
    booking_policies: str | None
    website: str | None
    support_email: str | None
    accent_color: str | None
    verification_state: str
    social_links: dict
    location: str | None
    firebase_uid: str | None
    is_public: bool
    created_at: datetime


class PractitionerPublicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    avatar_url: str | None
    cover_image_url: str | None
    logo_url: str | None
    bio: str | None
    profile_image: str | None
    category: str | None
    tagline: str | None
    specialties: list[str]
    booking_policies: str | None
    website: str | None
    support_email: str | None
    accent_color: str | None
    verification_state: str
    social_links: dict
    location: str | None
