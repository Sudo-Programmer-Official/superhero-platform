from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.types import AuthPrincipal
from app.models import Practitioner
from app.schemas.me import BootstrapPractitionerRequest, BootstrapPractitionerResponse, MeResponse


class MeService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_me(self, principal: AuthPrincipal) -> MeResponse:
        stmt = select(Practitioner).where(Practitioner.firebase_uid == principal.uid)
        practitioner = await self.session.scalar(stmt)

        return MeResponse(
            uid=principal.uid,
            email=principal.email,
            role=principal.role,
            practitioner_id=practitioner.id if practitioner else None,
            practitioner_name=practitioner.name if practitioner else None,
        )

    async def bootstrap_practitioner(
        self, principal: AuthPrincipal, payload: BootstrapPractitionerRequest
    ) -> BootstrapPractitionerResponse:
        if principal.role not in {"practitioner", "admin", "super_admin"}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role cannot bootstrap practitioner")

        existing = await self.session.scalar(select(Practitioner).where(Practitioner.firebase_uid == principal.uid))
        if existing:
            return BootstrapPractitionerResponse(practitioner_id=existing.id, created_at=existing.created_at)

        model = Practitioner(
            name=payload.name,
            bio=payload.bio,
            profile_image=payload.profile_image,
            location=payload.location,
            firebase_uid=principal.uid,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return BootstrapPractitionerResponse(practitioner_id=model.id, created_at=model.created_at)
