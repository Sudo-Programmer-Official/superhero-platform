from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_practitioner, require_tenant_access
from app.auth.types import AccessContext, AuthPrincipal
from app.db import get_db_session
from app.schemas.deal_card import DealCardCreate, DealCardRead, DealCardUpdate
from app.services.deal_card_service import DealCardService

router = APIRouter(prefix="/deal-cards", tags=["deal-cards"])


@router.get("", response_model=list[DealCardRead])
async def list_deal_cards(
    _: AccessContext = Depends(require_tenant_access("super_admin", "admin", "practitioner")),
    session: AsyncSession = Depends(get_db_session),
):
    return await DealCardService(session).list_deals()


@router.get("/public/{practitioner_slug}", response_model=list[DealCardRead])
async def list_public_deals(
    practitioner_slug: str,
    session: AsyncSession = Depends(get_db_session),
):
    return await DealCardService(session).list_public_deals_for_practitioner(practitioner_slug)


@router.get("/public/{practitioner_slug}/{deal_slug}", response_model=DealCardRead)
async def get_public_deal(
    practitioner_slug: str,
    deal_slug: str,
    session: AsyncSession = Depends(get_db_session),
):
    return await DealCardService(session).get_public_deal(practitioner_slug, deal_slug)


@router.post("", response_model=DealCardRead, status_code=status.HTTP_201_CREATED)
async def create_deal_card(
    payload: DealCardCreate,
    principal: AuthPrincipal = Depends(require_practitioner()),
    session: AsyncSession = Depends(get_db_session),
):
    return await DealCardService(session).create_deal(payload, principal)


@router.patch("/{deal_id}", response_model=DealCardRead)
async def update_deal_card(
    deal_id: UUID,
    payload: DealCardUpdate,
    principal: AuthPrincipal = Depends(require_practitioner()),
    session: AsyncSession = Depends(get_db_session),
):
    return await DealCardService(session).update_deal(deal_id, payload, principal)


@router.post("/{deal_id}/duplicate", response_model=DealCardRead, status_code=status.HTTP_201_CREATED)
async def duplicate_deal_card(
    deal_id: UUID,
    principal: AuthPrincipal = Depends(require_practitioner()),
    session: AsyncSession = Depends(get_db_session),
):
    return await DealCardService(session).duplicate_deal(deal_id, principal)


@router.post("/{deal_id}/archive", response_model=DealCardRead)
async def archive_deal_card(
    deal_id: UUID,
    principal: AuthPrincipal = Depends(require_practitioner()),
    session: AsyncSession = Depends(get_db_session),
):
    return await DealCardService(session).archive_deal(deal_id, principal)


@router.delete("/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal_card(
    deal_id: UUID,
    principal: AuthPrincipal = Depends(require_practitioner()),
    session: AsyncSession = Depends(get_db_session),
):
    await DealCardService(session).delete_deal(deal_id, principal)
