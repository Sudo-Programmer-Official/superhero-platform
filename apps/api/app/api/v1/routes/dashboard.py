from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_tenant_access
from app.auth.types import AccessContext
from app.db import get_db_session
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    access: AccessContext = Depends(
        require_tenant_access("super_admin", "admin", "operator", "finance_admin", "support_admin", "moderator", "practitioner")
    ),
    session: AsyncSession = Depends(get_db_session),
):
    return await DashboardService(session).get_summary(access)
