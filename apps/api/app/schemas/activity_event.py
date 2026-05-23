from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ActivityEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    tenant_id: str
    practitioner_id: str | None
    actor_id: str | None
    entity_type: str
    entity_id: str
    event_type: str
    metadata: dict = Field(alias="event_metadata")
    created_at: datetime


class ActivityEventPageRead(BaseModel):
    items: list[ActivityEventRead]
    next_cursor: str | None = None


class ActivityRetentionPruneRead(BaseModel):
    deleted_count: int
    retention_days: int
