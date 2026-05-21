from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Practitioner


class PractitionerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_all(self) -> list[Practitioner]:
        stmt: Select[tuple[Practitioner]] = select(Practitioner).order_by(Practitioner.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get(self, practitioner_id: UUID) -> Practitioner | None:
        return await self.session.get(Practitioner, practitioner_id)

    async def get_by_firebase_uid(self, firebase_uid: str) -> Practitioner | None:
        stmt: Select[tuple[Practitioner]] = select(Practitioner).where(Practitioner.firebase_uid == firebase_uid)
        return await self.session.scalar(stmt)

    async def get_by_stripe_account_id(self, stripe_account_id: str) -> Practitioner | None:
        stmt: Select[tuple[Practitioner]] = select(Practitioner).where(Practitioner.stripe_account_id == stripe_account_id)
        return await self.session.scalar(stmt)

    async def get_by_slug(self, slug: str) -> Practitioner | None:
        stmt: Select[tuple[Practitioner]] = select(Practitioner).where(Practitioner.slug == slug)
        return await self.session.scalar(stmt)

    async def create(self, model: Practitioner) -> Practitioner:
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return model

    async def delete(self, model: Practitioner) -> None:
        await self.session.delete(model)
