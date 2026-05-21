from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_principal, require_roles
from app.auth.types import AuthPrincipal
from app.db import get_db_session
from app.schemas.wallet_pass import (
    WalletPassExpireRequest,
    WalletPassIssueRequest,
    WalletPassRead,
    WalletPassRedeemRequest,
    WalletPassRestoreRequest,
)
from app.services.wallet_pass_service import WalletPassService

router = APIRouter(prefix="/wallet-passes", tags=["wallet-passes"])


@router.get("", response_model=list[WalletPassRead])
async def list_wallet_passes(
    _: AuthPrincipal = Depends(require_roles("super_admin", "admin", "practitioner")),
    session: AsyncSession = Depends(get_db_session),
):
    return await WalletPassService(session).list_wallet_passes()


@router.post("/issue", response_model=WalletPassRead)
async def issue_wallet_pass(
    payload: WalletPassIssueRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    return await WalletPassService(session).issue_wallet_pass(payload, principal)


@router.post("/redeem", response_model=WalletPassRead)
async def redeem_wallet_pass(
    payload: WalletPassRedeemRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    return await WalletPassService(session).redeem_by_qr(payload.qr_code, principal)


@router.post("/{wallet_pass_id}/expire", response_model=WalletPassRead)
async def expire_wallet_pass(
    wallet_pass_id: UUID,
    _: WalletPassExpireRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    return await WalletPassService(session).expire_wallet_pass(wallet_pass_id, principal)


@router.post("/{wallet_pass_id}/restore", response_model=WalletPassRead)
async def restore_wallet_pass(
    wallet_pass_id: UUID,
    _: WalletPassRestoreRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    return await WalletPassService(session).restore_wallet_pass(wallet_pass_id, principal)
