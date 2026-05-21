import uuid
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.types import AuthPrincipal
from app.models import WalletPass
from app.repositories.customer_repository import CustomerRepository
from app.repositories.deal_card_repository import DealCardRepository
from app.repositories.wallet_pass_repository import WalletPassRepository
from app.schemas.wallet_pass import WalletPassIssueRequest


class WalletPassService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = WalletPassRepository(session)
        self.deal_repo = DealCardRepository(session)
        self.customer_repo = CustomerRepository(session)

    async def list_wallet_passes(self) -> list[WalletPass]:
        return await self.repo.list_all()

    async def issue_wallet_pass(self, payload: WalletPassIssueRequest, principal: AuthPrincipal) -> WalletPass:
        if principal.role not in {"super_admin", "admin", "practitioner"}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role cannot issue wallet pass")

        deal = await self.deal_repo.get(payload.deal_id)
        if not deal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")

        customer = await self.customer_repo.get(payload.customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        model = WalletPass(
            deal_id=payload.deal_id,
            customer_id=payload.customer_id,
            qr_code=uuid.uuid4().hex,
            status="issued",
            wallet_type=payload.wallet_type,
        )
        created = await self.repo.create(model)
        await self.session.commit()
        return created

    async def redeem_by_qr(self, qr_code: str, principal: AuthPrincipal) -> WalletPass:
        if principal.role not in {"super_admin", "admin", "practitioner"}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role cannot redeem wallet pass")

        model = await self.repo.get_by_qr_code(qr_code)
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet pass not found")

        if model.status == "redeemed":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Wallet pass already redeemed")
        if model.status == "expired":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Wallet pass expired")

        model.status = "redeemed"
        model.redeemed_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def expire_wallet_pass(self, wallet_pass_id: UUID, principal: AuthPrincipal) -> WalletPass:
        if principal.role not in {"super_admin", "admin"}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role cannot expire wallet pass")

        model = await self.repo.get(wallet_pass_id)
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet pass not found")

        if model.status == "redeemed":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Redeemed wallet pass cannot be expired")

        model.status = "expired"
        await self.session.commit()
        await self.session.refresh(model)
        return model
