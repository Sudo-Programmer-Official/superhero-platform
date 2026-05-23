import uuid
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.types import AuthPrincipal
from app.domain_activity_events import ActivityEventType, EventScope, default_tenant
from app.models import WalletPass
from app.repositories.customer_repository import CustomerRepository
from app.repositories.deal_card_repository import DealCardRepository
from app.repositories.wallet_pass_repository import WalletPassRepository
from app.schemas.wallet_pass import WalletPassIssueRequest
from app.services.activity_pipeline import emit_activity_event


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
        deal_owner = await self.deal_repo.get(created.deal_id)
        scope = EventScope(
            tenant_id=default_tenant(),
            practitioner_id=str(deal_owner.practitioner_id) if deal_owner else None,
            actor_id=principal.uid,
        )
        await emit_activity_event(
            self.session,
            scope=scope,
            entity_type="wallet_pass",
            entity_id=str(created.id),
            event_type=ActivityEventType.WALLET_GENERATED,
            metadata={"deal_id": str(created.deal_id), "customer_id": str(created.customer_id), "wallet_pass_id": str(created.id)},
        )
        await self.session.commit()
        return created

    async def redeem_by_qr(self, qr_code: str, principal: AuthPrincipal) -> WalletPass:
        if principal.role not in {"super_admin", "admin", "practitioner"}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role cannot redeem wallet pass")

        model = await self.repo.get_by_qr_code(qr_code)
        if not model:
            await emit_activity_event(
                self.session,
                scope=EventScope(tenant_id=default_tenant(), practitioner_id=None, actor_id=principal.uid),
                entity_type="redemption",
                entity_id=qr_code[:32],
                event_type=ActivityEventType.REDEMPTION_FAILED,
                metadata={"reason": "not_found"},
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet pass not found")

        deal_owner = await self.deal_repo.get(model.deal_id)
        scope = EventScope(
            tenant_id=default_tenant(),
            practitioner_id=str(deal_owner.practitioner_id) if deal_owner else None,
            actor_id=principal.uid,
        )
        if model.status == "redeemed":
            await emit_activity_event(
                self.session,
                scope=scope,
                entity_type="redemption",
                entity_id=str(model.id),
                event_type=ActivityEventType.REDEMPTION_FAILED,
                metadata={"reason": "already_redeemed"},
            )
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Wallet pass already redeemed")
        if model.status == "expired":
            await emit_activity_event(
                self.session,
                scope=scope,
                entity_type="redemption",
                entity_id=str(model.id),
                event_type=ActivityEventType.REDEMPTION_FAILED,
                metadata={"reason": "expired"},
            )
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Wallet pass expired")

        model.status = "redeemed"
        model.redeemed_at = datetime.now(timezone.utc)
        await emit_activity_event(
            self.session,
            scope=scope,
            entity_type="wallet_pass",
            entity_id=str(model.id),
            event_type=ActivityEventType.WALLET_REDEEMED,
            metadata={"deal_id": str(model.deal_id), "customer_id": str(model.customer_id), "wallet_pass_id": str(model.id)},
        )
        await emit_activity_event(
            self.session,
            scope=scope,
            entity_type="redemption",
            entity_id=str(model.id),
            event_type=ActivityEventType.REDEMPTION_SUCCESS,
            metadata={"deal_id": str(model.deal_id), "customer_id": str(model.customer_id), "wallet_pass_id": str(model.id)},
        )
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

    async def restore_wallet_pass(self, wallet_pass_id: UUID, principal: AuthPrincipal) -> WalletPass:
        if principal.role not in {"super_admin", "admin", "practitioner"}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role cannot restore wallet pass")

        model = await self.repo.get(wallet_pass_id)
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet pass not found")

        if model.status not in {"expired", "inactive", "redeemed"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Wallet pass is already active")

        model.status = "issued"
        model.redeemed_at = None
        await self.session.commit()
        await self.session.refresh(model)
        return model
