from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from pydantic import Field


class ActivityEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    actor_id: str | None
    entity_type: str
    entity_id: str
    event_type: str
    metadata: dict = Field(validation_alias="event_metadata")
    created_at: datetime
