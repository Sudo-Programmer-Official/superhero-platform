from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Booking


class BookingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_all(self) -> list[Booking]:
        stmt: Select[tuple[Booking]] = select(Booking).order_by(Booking.booked_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_practitioner(self, practitioner_id: UUID) -> list[Booking]:
        stmt: Select[tuple[Booking]] = (
            select(Booking).where(Booking.practitioner_id == practitioner_id).order_by(Booking.booked_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get(self, booking_id: UUID) -> Booking | None:
        return await self.session.get(Booking, booking_id)

    async def create(self, model: Booking) -> Booking:
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return model
