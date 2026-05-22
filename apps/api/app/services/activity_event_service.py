from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ActivityEvent
from app.repositories.activity_event_repository import ActivityEventRepository


class ActivityEventService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ActivityEventRepository(session)

    async def track(
        self,
        *,
        actor_id: str | None,
        entity_type: str,
        entity_id: str,
        event_type: str,
        metadata: dict | None = None,
    ) -> ActivityEvent:
        model = ActivityEvent(
            actor_id=actor_id,
            entity_type=entity_type,
            entity_id=entity_id,
            event_type=event_type,
            event_metadata=metadata or {},
        )
        return await self.repo.create(model)

    async def list_recent(self, limit: int = 50) -> list[ActivityEvent]:
        return await self.repo.list_recent(limit=limit)
