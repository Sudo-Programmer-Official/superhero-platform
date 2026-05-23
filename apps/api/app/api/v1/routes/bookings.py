from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_tenant_access
from app.auth.types import AccessContext
from app.db import get_db_session
from app.schemas.booking import BookingRead
from app.services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("", response_model=list[BookingRead])
async def list_bookings(
    _: AccessContext = Depends(require_tenant_access("super_admin", "admin", "practitioner")),
    session: AsyncSession = Depends(get_db_session),
):
    return await BookingService(session).list_bookings()
