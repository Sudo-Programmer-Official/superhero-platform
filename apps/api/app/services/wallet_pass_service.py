import uuid
import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.types import AccessContext, AuthPrincipal
from app.domain_activity_events import ActivityEventType, EventScope, default_tenant
from app.models import Booking, Customer, DealCard, WalletPass
from app.repositories.customer_repository import CustomerRepository
from app.repositories.deal_card_repository import DealCardRepository
from app.repositories.wallet_pass_repository import WalletPassRepository
from app.schemas.wallet_pass import WalletPassIssueRequest
from app.services.activity_pipeline import emit_activity_event
from app.services.mail_service import MailService

logger = logging.getLogger("app.wallet_pass")


class WalletPassService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = WalletPassRepository(session)
        self.deal_repo = DealCardRepository(session)
        self.customer_repo = CustomerRepository(session)

    @staticmethod
    def _compute_redemption_status(model: WalletPass) -> str:
        if model.status == "redeemed":
            return "redeemed"
        if model.status in {"expired", "revoked"}:
            return model.status
        return "active"

    async def _to_wallet_payload(self, model: WalletPass) -> dict:
        provider = (model.wallet_type or "internal").strip().lower()
        booking = await self.session.get(Booking, model.booking_id) if model.booking_id else None
        deal = await self.session.get(DealCard, model.deal_id)
        customer = await self.session.get(Customer, model.customer_id)
        return {
            "id": model.id,
            "booking_id": model.booking_id,
            "deal_id": model.deal_id,
            "owner_id": model.customer_id,
            "customer_id": model.customer_id,
            "qr_code": model.qr_code,
            "pass_status": model.status,
            "status": model.status,
            "redemption_status": self._compute_redemption_status(model),
            "expires_at": model.expires_at,
            "redeemed_at": model.redeemed_at,
            "source_checkout_session_id": model.source_checkout_session_id,
            "wallet_provider": provider,
            "wallet_type": provider,
            "apple_wallet_url": model.apple_wallet_url,
            "google_wallet_url": model.google_wallet_url,
            "attendee_name": (booking.customer_name if booking and booking.customer_name else (customer.name if customer else None)),
            "attendee_email": (booking.customer_email if booking else (customer.email if customer else None)),
            "deal_title": deal.title if deal else None,
            "booking_number": booking.booking_number if booking else None,
            "created_at": model.created_at,
        }

    async def list_wallet_passes(self, access: AccessContext) -> list[dict]:
        try:
            if access.role == "practitioner":
                if not access.practitioner_id:
                    return []
                rows = await self.repo.list_by_practitioner(access.practitioner_id)
            else:
                rows = await self.repo.list_all()

            await emit_activity_event(
                self.session,
                scope=EventScope(
                    tenant_id=access.tenant_id,
                    practitioner_id=str(access.practitioner_id) if access.practitioner_id else None,
                    actor_id=access.principal.uid,
                ),
                entity_type="wallet_pass",
                entity_id="collection",
                event_type=ActivityEventType.WALLET_VIEWED,
                metadata={"count": len(rows)},
            )
            await self.session.commit()
            payloads: list[dict] = []
            for row in rows:
                payloads.append(await self._to_wallet_payload(row))
            return payloads
        except SQLAlchemyError as exc:
            await self.session.rollback()
            logger.exception("wallet.list.failed", extra={"event": "wallet.list.failed"})
            return []

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

    async def redeem_by_qr(self, qr_code: str, principal: AuthPrincipal) -> dict:
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
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "reason": "already_redeemed",
                    "redeemed_at": model.redeemed_at.isoformat() if model.redeemed_at else None,
                    "deal_id": str(model.deal_id),
                },
            )
        if model.status == "expired":
            await emit_activity_event(
                self.session,
                scope=scope,
                entity_type="redemption",
                entity_id=str(model.id),
                event_type=ActivityEventType.REDEMPTION_FAILED,
                metadata={"reason": "expired"},
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "reason": "expired",
                    "expires_at": model.expires_at.isoformat() if model.expires_at else None,
                    "deal_id": str(model.deal_id),
                },
            )

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
        booking = await self.session.get(Booking, model.booking_id) if model.booking_id else None
        deal = await self.session.get(DealCard, model.deal_id)
        customer = await self.session.get(Customer, model.customer_id)
        MailService.send_redemption_confirmation(
            customer_email=(booking.customer_email if booking else (customer.email if customer else None)),
            customer_name=(booking.customer_name if booking and booking.customer_name else (customer.name if customer else None)),
            deal_title=deal.title if deal else "OpenMat Experience",
            redeemed_at=model.redeemed_at.isoformat() if model.redeemed_at else datetime.now(timezone.utc).isoformat(),
        )
        return await self._to_wallet_payload(model)

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
