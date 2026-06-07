from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.types import AccessContext, AuthPrincipal
from app.models import DealCard
from app.repositories.deal_card_repository import DealCardRepository
from app.repositories.practitioner_repository import PractitionerRepository
from app.repositories.wallet_pass_repository import WalletPassRepository
from app.domain_activity_events import ActivityEventType, EventScope, default_tenant
from app.schemas.deal_card import DealCardCreate, DealCardUpdate
from app.services.activity_pipeline import emit_activity_event
from app.utils.slug import slugify


class DealCardService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = DealCardRepository(session)
        self.practitioner_repo = PractitionerRepository(session)
        self.wallet_repo = WalletPassRepository(session)

    async def list_deals(self, access: AccessContext) -> list[DealCard]:
        if access.role == "practitioner":
            if not access.practitioner_id:
                return []
            return await self.repo.list_by_practitioner(access.practitioner_id)
        return await self.repo.list_all()

    async def list_public_deals_for_practitioner(self, practitioner_slug: str) -> list[DealCard]:
        practitioner = await self.practitioner_repo.get_by_slug(practitioner_slug)
        if not practitioner or not practitioner.is_public:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practitioner not found")
        deals = await self.repo.list_by_practitioner(practitioner.id)
        return [d for d in deals if d.status in {"published", "expired", "canceled"}]

    async def get_public_deal(self, practitioner_slug: str, deal_slug: str) -> DealCard:
        practitioner = await self.practitioner_repo.get_by_slug(practitioner_slug)
        if not practitioner or not practitioner.is_public:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practitioner not found")
        deal = await self.repo.get_by_slug(deal_slug)
        if not deal or deal.practitioner_id != practitioner.id or deal.status not in {"published", "expired", "canceled"}:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
        return deal

    async def create_deal(self, payload: DealCardCreate, principal: AuthPrincipal) -> DealCard:
        practitioner = await self.practitioner_repo.get(payload.practitioner_id)
        if not practitioner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practitioner not found")

        if principal.role == "practitioner" and practitioner.firebase_uid != principal.uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create deal for another practitioner")

        base_slug = slugify(payload.title)
        slug = base_slug
        i = 1
        while await self.repo.get_by_slug(slug):
            i += 1
            slug = f"{base_slug}-{i}"

        model = DealCard(
            practitioner_id=payload.practitioner_id,
            title=payload.title,
            slug=slug,
            cta_text=payload.cta_text,
            booking_url=payload.booking_url,
            description=payload.description,
            image=payload.image,
            price=payload.price,
            capacity=payload.capacity,
            remaining_slots=payload.capacity,
            location=payload.location,
            timezone=payload.timezone,
            start_time=payload.start_time,
            end_time=payload.end_time,
            expiration_time=payload.expiration_time,
            share_link=None,
            status="draft",
            wallet_enabled=payload.wallet_enabled,
        )
        created = await self.repo.create(model)
        await emit_activity_event(
            self.session,
            scope=EventScope(tenant_id=default_tenant(), practitioner_id=str(created.practitioner_id), actor_id=principal.uid),
            entity_type="deal",
            entity_id=str(created.id),
            event_type=ActivityEventType.DEAL_CREATED,
            metadata={"deal_title": created.title, "deal_slug": created.slug, "status": created.status, "seats": created.capacity},
        )
        await self.session.commit()
        return created

    async def update_deal(self, deal_id: UUID, payload: DealCardUpdate, principal: AuthPrincipal) -> DealCard:
        model = await self.repo.get(deal_id)
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")

        if principal.role == "practitioner":
            practitioner = await self.practitioner_repo.get(model.practitioner_id)
            if not practitioner or practitioner.firebase_uid != principal.uid:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify this deal")

        for field, value in payload.model_dump(exclude_unset=True).items():
            if field == "status" and value not in {"draft", "published", "expired", "canceled"}:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid deal status")
            setattr(model, field, value)

        if payload.status == "published":
            practitioner = await self.practitioner_repo.get(model.practitioner_id)
            if not practitioner:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practitioner not found")
            model.share_link = f"/openmat/{practitioner.slug}/{model.slug}"
            await emit_activity_event(
                self.session,
                scope=EventScope(tenant_id=default_tenant(), practitioner_id=str(model.practitioner_id), actor_id=principal.uid),
                entity_type="deal",
                entity_id=str(model.id),
                event_type=ActivityEventType.DEAL_PUBLISHED,
                metadata={"deal_title": model.title, "deal_slug": model.slug, "public_url": model.share_link},
            )
        elif payload.status in {"expired", "canceled"}:
            wallet_passes = await self.wallet_repo.list_by_deal_id(model.id)
            for wallet_pass in wallet_passes:
                if wallet_pass.status not in {"redeemed"}:
                    wallet_pass.status = "inactive"
            await emit_activity_event(
                self.session,
                scope=EventScope(tenant_id=default_tenant(), practitioner_id=str(model.practitioner_id), actor_id=principal.uid),
                entity_type="deal",
                entity_id=str(model.id),
                event_type=ActivityEventType.DEAL_ARCHIVED,
                metadata={"deal_title": model.title, "deal_slug": model.slug, "status": payload.status},
            )

        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def duplicate_deal(self, deal_id: UUID, principal: AuthPrincipal) -> DealCard:
        source = await self.repo.get(deal_id)
        if not source:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")

        if principal.role == "practitioner":
            practitioner = await self.practitioner_repo.get(source.practitioner_id)
            if not practitioner or practitioner.firebase_uid != principal.uid:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot duplicate this deal")

        base_slug = slugify(f"{source.title}-copy")
        slug = base_slug
        i = 1
        while await self.repo.get_by_slug(slug):
            i += 1
            slug = f"{base_slug}-{i}"

        model = DealCard(
            practitioner_id=source.practitioner_id,
            title=f"{source.title} (Copy)",
            slug=slug,
            cta_text=source.cta_text,
            booking_url=source.booking_url,
            description=source.description,
            image=source.image,
            price=source.price,
            capacity=source.capacity,
            remaining_slots=source.capacity,
            location=source.location,
            timezone=source.timezone,
            start_time=source.start_time,
            end_time=source.end_time,
            expiration_time=source.expiration_time,
            share_link=None,
            status="draft",
            wallet_enabled=source.wallet_enabled,
        )
        created = await self.repo.create(model)
        await emit_activity_event(
            self.session,
            scope=EventScope(tenant_id=default_tenant(), practitioner_id=str(created.practitioner_id), actor_id=principal.uid),
            entity_type="deal",
            entity_id=str(created.id),
            event_type=ActivityEventType.DEAL_DUPLICATED,
            metadata={"source_deal_id": str(source.id), "deal_title": created.title, "deal_slug": created.slug},
        )
        await self.session.commit()
        return created

    async def archive_deal(self, deal_id: UUID, principal: AuthPrincipal) -> DealCard:
        model = await self.repo.get(deal_id)
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")

        if principal.role == "practitioner":
            practitioner = await self.practitioner_repo.get(model.practitioner_id)
            if not practitioner or practitioner.firebase_uid != principal.uid:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot archive this deal")

        model.status = "canceled"
        model.share_link = None

        wallet_passes = await self.wallet_repo.list_by_deal_id(model.id)
        for wallet_pass in wallet_passes:
            if wallet_pass.status not in {"redeemed"}:
                wallet_pass.status = "inactive"

        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def delete_deal(self, deal_id: UUID, principal: AuthPrincipal) -> None:
        model = await self.repo.get(deal_id)
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")

        if principal.role == "practitioner":
            practitioner = await self.practitioner_repo.get(model.practitioner_id)
            if not practitioner or practitioner.firebase_uid != principal.uid:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete this deal")

        await self.repo.delete(model)
        await self.session.commit()
