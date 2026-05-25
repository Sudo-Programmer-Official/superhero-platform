from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_roles
from app.auth.types import AuthPrincipal
from app.db import get_db_session
from app.schemas.admin_ops import (
    AdminBookingRow,
    AdminDealActionRequest,
    AdminDealRow,
    AdminPayoutActionRequest,
    AdminPayoutRow,
    AdminPractitionerActionRequest,
    AdminPractitionerRow,
    AdminRedemptionRow,
    AdminTimelineEventRow,
    AdminWalletPassRow,
)
from app.services.admin_ops_service import AdminOpsService

router = APIRouter(prefix="/admin", tags=["admin-ops"])


@router.get("/practitioners", response_model=list[AdminPractitionerRow])
async def list_admin_practitioners(
    query: str | None = Query(default=None),
    _: AuthPrincipal = Depends(require_roles("super_admin", "admin", "operator", "support_admin")),
    session: AsyncSession = Depends(get_db_session),
):
    return await AdminOpsService(session).list_practitioners(query=query)


@router.post("/practitioners/{practitioner_id}/actions", response_model=AdminPractitionerRow)
async def practitioner_action(
    practitioner_id: UUID,
    payload: AdminPractitionerActionRequest,
    _: AuthPrincipal = Depends(require_roles("super_admin", "admin", "operator", "support_admin")),
    session: AsyncSession = Depends(get_db_session),
):
    return await AdminOpsService(session).apply_practitioner_action(practitioner_id=practitioner_id, action=payload.action)


@router.get("/deals", response_model=list[AdminDealRow])
async def list_admin_deals(
    query: str | None = Query(default=None),
    status: str | None = Query(default=None),
    _: AuthPrincipal = Depends(require_roles("super_admin", "admin", "operator", "moderator")),
    session: AsyncSession = Depends(get_db_session),
):
    return await AdminOpsService(session).list_deals(query=query, deal_status=status)


@router.post("/deals/{deal_id}/actions", response_model=AdminDealRow)
async def deal_action(
    deal_id: UUID,
    payload: AdminDealActionRequest,
    _: AuthPrincipal = Depends(require_roles("super_admin", "admin", "operator", "moderator")),
    session: AsyncSession = Depends(get_db_session),
):
    return await AdminOpsService(session).apply_deal_action(deal_id=deal_id, action=payload.action)


@router.get("/payouts", response_model=list[AdminPayoutRow])
async def list_admin_payouts(
    query: str | None = Query(default=None),
    status: str | None = Query(default=None),
    _: AuthPrincipal = Depends(require_roles("super_admin", "finance_admin")),
    session: AsyncSession = Depends(get_db_session),
):
    return await AdminOpsService(session).list_payouts(query=query, payout_status=status)


@router.post("/payouts/{practitioner_id}/actions", response_model=AdminPayoutRow)
async def payout_action(
    practitioner_id: UUID,
    payload: AdminPayoutActionRequest,
    _: AuthPrincipal = Depends(require_roles("super_admin", "finance_admin")),
    session: AsyncSession = Depends(get_db_session),
):
    return await AdminOpsService(session).apply_payout_action(practitioner_id=practitioner_id, action=payload.action)


@router.get("/bookings", response_model=list[AdminBookingRow])
async def list_admin_bookings(
    query: str | None = Query(default=None),
    payment_status: str | None = Query(default=None, alias="status"),
    _: AuthPrincipal = Depends(require_roles("super_admin", "admin", "operator", "finance_admin", "support_admin")),
    session: AsyncSession = Depends(get_db_session),
):
    return await AdminOpsService(session).list_bookings(query=query, payment_status=payment_status)


@router.get("/wallet-passes", response_model=list[AdminWalletPassRow])
async def list_admin_wallet_passes(
    query: str | None = Query(default=None),
    pass_status: str | None = Query(default=None, alias="status"),
    _: AuthPrincipal = Depends(require_roles("super_admin", "admin", "operator", "support_admin", "moderator")),
    session: AsyncSession = Depends(get_db_session),
):
    return await AdminOpsService(session).list_wallet_passes(query=query, pass_status=pass_status)


@router.get("/redemptions", response_model=list[AdminRedemptionRow])
async def list_admin_redemptions(
    query: str | None = Query(default=None),
    window: str | None = Query(default="24h"),
    _: AuthPrincipal = Depends(require_roles("super_admin", "admin", "operator", "support_admin", "moderator")),
    session: AsyncSession = Depends(get_db_session),
):
    return await AdminOpsService(session).list_redemptions(query=query, window=window)


@router.get("/timeline", response_model=list[AdminTimelineEventRow])
async def list_admin_timeline(
    entity_type: str,
    entity_id: str,
    limit: int = Query(default=80, ge=1, le=200),
    _: AuthPrincipal = Depends(require_roles("super_admin", "admin", "operator", "support_admin", "moderator")),
    session: AsyncSession = Depends(get_db_session),
):
    return await AdminOpsService(session).list_timeline(entity_type=entity_type, entity_id=entity_id, limit=limit)
