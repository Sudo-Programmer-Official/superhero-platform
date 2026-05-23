from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_authenticated_user
from app.auth.types import AuthPrincipal
from app.db import get_db_session
from app.schemas.me import BootstrapPractitionerRequest, BootstrapPractitionerResponse, MeResponse
from app.services.me_service import MeService

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=MeResponse)
async def me(
    principal: AuthPrincipal = Depends(require_authenticated_user),
    session: AsyncSession = Depends(get_db_session),
):
    return await MeService(session).get_me(principal)


@router.post("/bootstrap-practitioner", response_model=BootstrapPractitionerResponse)
async def bootstrap_practitioner(
    payload: BootstrapPractitionerRequest,
    principal: AuthPrincipal = Depends(require_authenticated_user),
    session: AsyncSession = Depends(get_db_session),
):
    return await MeService(session).bootstrap_practitioner(principal, payload)
