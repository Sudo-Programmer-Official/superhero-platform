from datetime import UTC, datetime, timedelta

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
        tenant_id: str,
        practitioner_id: str | None,
        actor_id: str | None,
        entity_type: str,
        entity_id: str,
        event_type: str,
        metadata: dict | None = None,
    ) -> ActivityEvent:
        model = ActivityEvent(
            tenant_id=tenant_id,
            practitioner_id=practitioner_id,
            actor_id=actor_id,
            entity_type=entity_type,
            entity_id=entity_id,
            event_type=event_type,
            event_metadata=metadata or {},
        )
        return await self.repo.create(model)

    async def list_recent(
        self,
        *,
        tenant_id: str,
        practitioner_id: str | None,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[ActivityEvent], str | None]:
        return await self.repo.list_recent(
            tenant_id=tenant_id,
            practitioner_id=practitioner_id,
            limit=limit,
            cursor=cursor,
        )

    async def prune_retention(
        self,
        *,
        tenant_id: str,
        retention_days: int,
        now: datetime | None = None,
    ) -> int:
        reference = now or datetime.now(UTC)
        cutoff = reference - timedelta(days=max(1, retention_days))
        return await self.repo.delete_before(tenant_id=tenant_id, cutoff=cutoff)
