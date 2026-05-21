from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DealCard


class DealCardRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_all(self) -> list[DealCard]:
        stmt: Select[tuple[DealCard]] = select(DealCard).order_by(DealCard.start_time.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get(self, deal_id: UUID) -> DealCard | None:
        return await self.session.get(DealCard, deal_id)

    async def create(self, model: DealCard) -> DealCard:
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return model

    async def delete(self, model: DealCard) -> None:
        await self.session.delete(model)
