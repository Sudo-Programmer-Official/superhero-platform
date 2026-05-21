from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_principal, require_roles
from app.auth.types import AuthPrincipal
from app.db import get_db_session
from app.schemas.practitioner import PractitionerCreate, PractitionerRead, PractitionerUpdate
from app.services.practitioner_service import PractitionerService

router = APIRouter(prefix="/practitioners", tags=["practitioners"])


@router.get("", response_model=list[PractitionerRead])
async def list_practitioners(
    _: AuthPrincipal = Depends(require_roles("super_admin", "admin")),
    session: AsyncSession = Depends(get_db_session),
):
    return await PractitionerService(session).list_practitioners()


@router.post("", response_model=PractitionerRead, status_code=status.HTTP_201_CREATED)
async def create_practitioner(
    payload: PractitionerCreate,
    principal: AuthPrincipal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    firebase_uid = principal.uid if principal.role in {"practitioner", "super_admin", "admin"} else None
    return await PractitionerService(session).create_practitioner(payload, firebase_uid)


@router.patch("/{practitioner_id}", response_model=PractitionerRead)
async def update_practitioner(
    practitioner_id: UUID,
    payload: PractitionerUpdate,
    _: AuthPrincipal = Depends(require_roles("super_admin", "admin", "practitioner")),
    session: AsyncSession = Depends(get_db_session),
):
    return await PractitionerService(session).update_practitioner(practitioner_id, payload)


@router.delete("/{practitioner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_practitioner(
    practitioner_id: UUID,
    _: AuthPrincipal = Depends(require_roles("super_admin", "admin")),
    session: AsyncSession = Depends(get_db_session),
):
    await PractitionerService(session).delete_practitioner(practitioner_id)
