from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.types import AuthPrincipal
from app.domain.permissions import BOOTSTRAP_ROLES, normalize_effective_role
from app.models import Practitioner
from app.schemas.me import BootstrapPractitionerRequest, BootstrapPractitionerResponse, MeResponse
from app.utils.slug import slugify


class MeService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_me(self, principal: AuthPrincipal) -> MeResponse:
        stmt = select(Practitioner).where(Practitioner.firebase_uid == principal.uid)
        practitioner = await self.session.scalar(stmt)
        effective_role = normalize_effective_role(principal.role, bool(practitioner))

        return MeResponse(
            uid=principal.uid,
            email=principal.email,
            role=effective_role,
            practitioner_id=practitioner.id if practitioner else None,
            practitioner_name=practitioner.name if practitioner else None,
            practitioner_slug=practitioner.slug if practitioner else None,
            stripe_account_id=practitioner.stripe_account_id if practitioner else None,
            onboarding_state=(
                "connected"
                if practitioner and practitioner.stripe_account_id and practitioner.stripe_onboarding_complete
                else "onboarding"
                if practitioner and practitioner.stripe_account_id
                else "not_connected"
            ),
            payouts_enabled=bool(practitioner and practitioner.stripe_onboarding_complete),
            charges_enabled=bool(practitioner and practitioner.stripe_onboarding_complete),
        )

    async def bootstrap_practitioner(
        self, principal: AuthPrincipal, payload: BootstrapPractitionerRequest
    ) -> BootstrapPractitionerResponse:
        # New Firebase users typically start as "customer"; allow them to bootstrap their own practitioner profile.
        if principal.role not in BOOTSTRAP_ROLES:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role cannot bootstrap practitioner")

        existing = await self.session.scalar(select(Practitioner).where(Practitioner.firebase_uid == principal.uid))
        if existing:
            return BootstrapPractitionerResponse(practitioner_id=existing.id, created_at=existing.created_at)

        base_slug = slugify(payload.name)
        slug = base_slug
        i = 1
        while await self.session.scalar(select(Practitioner).where(Practitioner.slug == slug)):
            i += 1
            slug = f"{base_slug}-{i}"

        model = Practitioner(
            name=payload.name,
            slug=slug,
            bio=payload.bio,
            profile_image=payload.profile_image,
            location=payload.location,
            firebase_uid=principal.uid,
            is_public=True,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return BootstrapPractitionerResponse(practitioner_id=model.id, created_at=model.created_at)
