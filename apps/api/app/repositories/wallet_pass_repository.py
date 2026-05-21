from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import WalletPass


class WalletPassRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_all(self) -> list[WalletPass]:
        stmt: Select[tuple[WalletPass]] = select(WalletPass).order_by(WalletPass.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get(self, wallet_pass_id: UUID) -> WalletPass | None:
        return await self.session.get(WalletPass, wallet_pass_id)

    async def get_by_qr_code(self, qr_code: str) -> WalletPass | None:
        stmt: Select[tuple[WalletPass]] = select(WalletPass).where(WalletPass.qr_code == qr_code)
        return await self.session.scalar(stmt)

    async def get_by_checkout_session_id(self, checkout_session_id: str) -> WalletPass | None:
        stmt: Select[tuple[WalletPass]] = select(WalletPass).where(
            WalletPass.source_checkout_session_id == checkout_session_id
        )
        return await self.session.scalar(stmt)

    async def list_by_deal_id(self, deal_id: UUID) -> list[WalletPass]:
        stmt: Select[tuple[WalletPass]] = select(WalletPass).where(WalletPass.deal_id == deal_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, model: WalletPass) -> WalletPass:
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return model
