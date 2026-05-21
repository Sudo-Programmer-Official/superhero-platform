from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Practitioner
from app.repositories.practitioner_repository import PractitionerRepository
from app.schemas.practitioner import PractitionerCreate, PractitionerUpdate


class PractitionerService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PractitionerRepository(session)

    async def list_practitioners(self) -> list[Practitioner]:
        return await self.repo.list_all()

    async def create_practitioner(self, payload: PractitionerCreate, firebase_uid: str | None) -> Practitioner:
        model = Practitioner(
            name=payload.name,
            bio=payload.bio,
            profile_image=payload.profile_image,
            location=payload.location,
            firebase_uid=firebase_uid,
        )
        created = await self.repo.create(model)
        await self.session.commit()
        return created

    async def update_practitioner(self, practitioner_id: UUID, payload: PractitionerUpdate) -> Practitioner:
        model = await self.repo.get(practitioner_id)
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practitioner not found")

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(model, field, value)

        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def delete_practitioner(self, practitioner_id: UUID) -> None:
        model = await self.repo.get(practitioner_id)
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practitioner not found")
        await self.repo.delete(model)
        await self.session.commit()
