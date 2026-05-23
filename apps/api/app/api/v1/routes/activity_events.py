from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_tenant_access
from app.auth.types import AccessContext
from app.config import settings
from app.db import get_db_session
from app.schemas.activity_event import ActivityEventPageRead, ActivityRetentionPruneRead
from app.services.activity_event_service import ActivityEventService

router = APIRouter(prefix="/activity-events", tags=["activity-events"])


@router.get("", response_model=ActivityEventPageRead)
async def list_activity_events(
    ctx: AccessContext = Depends(require_tenant_access("super_admin", "admin", "practitioner")),
    limit: int = Query(default=40, ge=1, le=200),
    cursor: str | None = Query(default=None),
    session: AsyncSession = Depends(get_db_session),
):
    practitioner_id = str(ctx.practitioner_id) if ctx.role == "practitioner" and ctx.practitioner_id else None
    items, next_cursor = await ActivityEventService(session).list_recent(
        tenant_id=ctx.tenant_id,
        practitioner_id=practitioner_id,
        limit=limit,
        cursor=cursor,
    )
    return ActivityEventPageRead(items=items, next_cursor=next_cursor)


@router.post("/retention/prune", response_model=ActivityRetentionPruneRead)
async def prune_activity_events(
    ctx: AccessContext = Depends(require_tenant_access("super_admin", "admin")),
    session: AsyncSession = Depends(get_db_session),
):
    deleted_count = await ActivityEventService(session).prune_retention(
        tenant_id=ctx.tenant_id,
        retention_days=settings.activity_event_retention_days,
    )
    return ActivityRetentionPruneRead(
        deleted_count=deleted_count,
        retention_days=settings.activity_event_retention_days,
    )
