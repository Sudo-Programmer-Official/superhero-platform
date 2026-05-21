from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_principal, require_roles
from app.auth.types import AuthPrincipal
from app.db import get_db_session
from app.schemas.stripe_connect import StripeConnectStartRequest, StripeConnectStartResponse, StripeConnectStatusResponse
from app.services.stripe_connect_service import StripeConnectService

router = APIRouter(prefix="/stripe-connect", tags=["stripe-connect"])


@router.post("/start", response_model=StripeConnectStartResponse)
async def start_stripe_connect(
    payload: StripeConnectStartRequest,
    principal: AuthPrincipal = Depends(require_roles("practitioner", "admin", "super_admin")),
    session: AsyncSession = Depends(get_db_session),
):
    return await StripeConnectService(session).start_onboarding(payload, principal)


@router.get("/status", response_model=StripeConnectStatusResponse)
async def stripe_connect_status(
    principal: AuthPrincipal = Depends(require_roles("practitioner", "admin", "super_admin")),
    session: AsyncSession = Depends(get_db_session),
):
    return await StripeConnectService(session).get_status(principal)
