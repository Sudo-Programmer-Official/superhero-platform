from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Customer


class CustomerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, customer_id: UUID) -> Customer | None:
        return await self.session.get(Customer, customer_id)
