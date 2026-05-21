from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DealCard, Practitioner, WalletPass
from app.schemas.tenant import TenantSummary


class TenantService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_summary(self) -> TenantSummary:
        practitioner_count = await self.session.scalar(select(func.count(Practitioner.id))) or 0
        deal_count = await self.session.scalar(select(func.count(DealCard.id))) or 0
        wallet_pass_count = await self.session.scalar(select(func.count(WalletPass.id))) or 0
        return TenantSummary(
            practitioner_count=int(practitioner_count),
            deal_count=int(deal_count),
            wallet_pass_count=int(wallet_pass_count),
        )
