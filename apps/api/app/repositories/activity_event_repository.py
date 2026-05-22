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

    async def list_recent(self, limit: int = 50) -> list[ActivityEvent]:
        stmt: Select[tuple[ActivityEvent]] = select(ActivityEvent).order_by(ActivityEvent.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
