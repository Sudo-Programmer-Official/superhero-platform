from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.types import AccessContext
from app.models import Booking
from app.repositories.booking_repository import BookingRepository


class BookingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = BookingRepository(session)

    async def list_bookings(self, access: AccessContext) -> list[Booking]:
        if access.practitioner_id:
            return await self.repo.list_by_practitioner(access.practitioner_id)
        return await self.repo.list_all()
