from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_roles
from app.auth.types import AuthPrincipal
from app.db import get_db_session
from app.schemas.tenant import TenantSummary
from app.services.tenant_service import TenantService

router = APIRouter(prefix="/super-admin", tags=["super-admin"])


@router.get("/tenant-summary", response_model=TenantSummary)
async def tenant_summary(
    _: AuthPrincipal = Depends(require_roles("super_admin")),
    session: AsyncSession = Depends(get_db_session),
):
    return await TenantService(session).get_summary()
