from datetime import datetime

from sqlalchemy import delete
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ActivityEvent


class ActivityEventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, model: ActivityEvent) -> ActivityEvent:
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return model

    async def list_recent(
        self,
        *,
        tenant_id: str,
        practitioner_id: str | None,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[ActivityEvent], str | None]:
        stmt: Select[tuple[ActivityEvent]] = (
            select(ActivityEvent)
            .where(ActivityEvent.tenant_id == tenant_id)
            .order_by(ActivityEvent.created_at.desc(), ActivityEvent.id.desc())
        )
        if practitioner_id:
            stmt = stmt.where(ActivityEvent.practitioner_id == practitioner_id)
        if cursor:
            try:
                cursor_dt = datetime.fromisoformat(cursor.replace("Z", "+00:00"))
                stmt = stmt.where(ActivityEvent.created_at < cursor_dt)
            except ValueError:
                pass

        stmt = stmt.limit(limit + 1)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        has_more = len(rows) > limit
        items = rows[:limit]
        next_cursor = items[-1].created_at.isoformat() if has_more and items else None
        return items, next_cursor

    async def delete_before(
        self,
        *,
        tenant_id: str,
        cutoff: datetime,
    ) -> int:
        stmt = (
            delete(ActivityEvent)
            .where(ActivityEvent.tenant_id == tenant_id)
            .where(ActivityEvent.created_at < cutoff)
        )
        result = await self.session.execute(stmt)
        return int(result.rowcount or 0)
