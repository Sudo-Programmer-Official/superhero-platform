from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Practitioner
from app.auth.types import AuthPrincipal
from app.repositories.practitioner_repository import PractitionerRepository
from app.schemas.practitioner import PractitionerCreate, PractitionerUpdate
from app.utils.slug import slugify


class PractitionerService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PractitionerRepository(session)

    async def list_practitioners(self) -> list[Practitioner]:
        return await self.repo.list_all()

    async def create_practitioner(self, payload: PractitionerCreate, firebase_uid: str | None) -> Practitioner:
        base_slug = slugify(payload.name)
        slug = base_slug
        i = 1
        while await self.repo.get_by_slug(slug):
            i += 1
            slug = f"{base_slug}-{i}"

        model = Practitioner(
            name=payload.name,
            slug=slug,
            bio=payload.bio,
            profile_image=payload.profile_image,
            location=payload.location,
            firebase_uid=firebase_uid,
            is_public=True,
            social_links={"instagram": None, "tiktok": None, "youtube": None, "linkedin": None, "website": None},
            branding={
                "cover_image_url": None,
                "logo_url": None,
                "category": None,
                "tagline": None,
                "specialties": [],
                "booking_policies": None,
                "support_email": None,
                "accent_color": "#f4d8a7",
                "verification_state": "unverified",
            },
        )
        created = await self.repo.create(model)
        await self.session.commit()
        return created

    async def update_practitioner(
        self, practitioner_id: UUID, payload: PractitionerUpdate, principal: AuthPrincipal
    ) -> Practitioner:
        model = await self.repo.get(practitioner_id)
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practitioner not found")

        # Admins can update any practitioner. Other authenticated users may only update their own profile.
        if principal.role not in {"super_admin", "admin"} and model.firebase_uid != principal.uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")

        patch = payload.model_dump(exclude_unset=True)

        if "name" in patch:
            model.name = patch["name"]
        if "bio" in patch:
            model.bio = patch["bio"]
        if "location" in patch:
            model.location = patch["location"]

        if "profile_image" in patch:
            model.profile_image = patch["profile_image"]
        if "avatar_url" in patch:
            model.profile_image = patch["avatar_url"]

        if "slug" in patch and patch["slug"]:
            base_slug = slugify(patch["slug"])
            slug = base_slug
            i = 1
            while True:
                existing = await self.repo.get_by_slug(slug)
                if not existing or existing.id == model.id:
                    break
                i += 1
                slug = f"{base_slug}-{i}"
            model.slug = slug

        social = dict(model.social_links or {})
        branding = dict(model.branding or {})

        if "social_links" in patch and patch["social_links"]:
            social.update(patch["social_links"])
        if "website" in patch:
            social["website"] = patch["website"]
        model.social_links = social

        branding_map = {
            "cover_image_url": "cover_image_url",
            "logo_url": "logo_url",
            "category": "category",
            "tagline": "tagline",
            "specialties": "specialties",
            "booking_policies": "booking_policies",
            "support_email": "support_email",
            "accent_color": "accent_color",
            "verification_state": "verification_state",
        }
        for in_key, out_key in branding_map.items():
            if in_key in patch:
                branding[out_key] = patch[in_key]
        model.branding = branding

        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def get_public_practitioner(self, slug: str) -> Practitioner:
        model = await self.repo.get_by_slug(slug)
        if not model or not model.is_public:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practitioner not found")
        return model

    async def delete_practitioner(self, practitioner_id: UUID) -> None:
        model = await self.repo.get(practitioner_id)
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practitioner not found")
        await self.repo.delete(model)
        await self.session.commit()
