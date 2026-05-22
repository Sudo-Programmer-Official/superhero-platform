from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_roles
from app.auth.types import AuthPrincipal
from app.db import get_db_session
from app.schemas.activity_event import ActivityEventRead
from app.services.activity_event_service import ActivityEventService

router = APIRouter(prefix="/activity-events", tags=["activity-events"])


@router.get("", response_model=list[ActivityEventRead])
async def list_activity_events(
    _: AuthPrincipal = Depends(require_roles("super_admin", "admin", "practitioner")),
    session: AsyncSession = Depends(get_db_session),
):
    return await ActivityEventService(session).list_recent(limit=80)
