from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MeResponse(BaseModel):
    uid: str
    email: str | None
    role: str
    practitioner_id: UUID | None = None
    practitioner_name: str | None = None
    practitioner_slug: str | None = None
    stripe_account_id: str | None = None
    onboarding_state: str = "not_connected"
    payouts_enabled: bool = False
    charges_enabled: bool = False


class BootstrapPractitionerRequest(BaseModel):
    name: str
    bio: str | None = None
    profile_image: str | None = None
    location: str | None = None


class BootstrapPractitionerResponse(BaseModel):
    practitioner_id: UUID
    created_at: datetime
