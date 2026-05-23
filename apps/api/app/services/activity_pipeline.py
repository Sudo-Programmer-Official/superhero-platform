from sqlalchemy.ext.asyncio import AsyncSession

from app.domain_activity_events import EventScope
from app.services.activity_event_service import ActivityEventService


async def emit_activity_event(
    session: AsyncSession,
    *,
    scope: EventScope,
    entity_type: str,
    entity_id: str,
    event_type: str,
    metadata: dict | None = None,
) -> None:
    service = ActivityEventService(session)
    await service.track(
        tenant_id=scope.tenant_id,
        practitioner_id=scope.practitioner_id,
        actor_id=scope.actor_id,
        entity_type=entity_type,
        entity_id=entity_id,
        event_type=event_type,
        metadata=metadata or {},
    )
