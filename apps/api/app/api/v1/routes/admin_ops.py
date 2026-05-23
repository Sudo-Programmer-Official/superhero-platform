from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_roles
from app.auth.types import AuthPrincipal
from app.db import get_db_session
from app.schemas.admin_ops import (
    AdminDealActionRequest,
    AdminDealRow,
    AdminPayoutActionRequest,
    AdminPayoutRow,
    AdminPractitionerActionRequest,
    AdminPractitionerRow,
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
