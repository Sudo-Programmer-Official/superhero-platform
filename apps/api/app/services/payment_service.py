from __future__ import annotations

import uuid
from decimal import Decimal
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import stripe
from fastapi import HTTPException, status
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.domain_activity_events import ActivityEventType, EventScope, default_tenant
from app.models import Booking, Customer, WalletPass
from app.repositories.deal_card_repository import DealCardRepository
from app.repositories.practitioner_repository import PractitionerRepository
from app.repositories.wallet_pass_repository import WalletPassRepository
from app.schemas.payment import CheckoutSessionCreateRequest, CheckoutSessionCreateResponse, CheckoutSessionResultResponse
from app.services.activity_pipeline import emit_activity_event
from app.services.mail_service import MailService


class PaymentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.deal_repo = DealCardRepository(session)
        self.practitioner_repo = PractitionerRepository(session)
        self.wallet_repo = WalletPassRepository(session)
        stripe.api_key = settings.stripe_secret_key

    def _assert_configured(self) -> None:
        if settings.payments_test_mode or settings.demo_checkout_mode:
            return
        if not settings.stripe_secret_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stripe secret key not configured",
            )

    @staticmethod
    def _append_query(url: str, params: dict[str, str]) -> str:
        split = urlsplit(url)
        query = dict(parse_qsl(split.query))
        query.update(params)
        return urlunsplit((split.scheme, split.netloc, split.path, urlencode(query), split.fragment))

    async def _get_or_create_customer(self, email: str, name: str | None) -> Customer:
        existing = await self.session.scalar(select(Customer).where(Customer.email == email))
        if existing:
            return existing
        customer = Customer(email=email, name=name)
        self.session.add(customer)
        await self.session.flush()
        await self.session.refresh(customer)
        return customer

    async def _finalize_paid_checkout(
        self,
        checkout_session_id: str,
        deal_id: uuid.UUID,
        customer_id: uuid.UUID,
        quantity: int = 1,
    ) -> None:
        try:
            existing = await self.wallet_repo.get_by_checkout_session_id(checkout_session_id)
            if existing:
                return

            deal = await self.deal_repo.get(deal_id)
            if not deal or deal.remaining_slots <= 0:
                return

            practitioner = await self.practitioner_repo.get(deal.practitioner_id)
            customer = await self.session.get(Customer, customer_id)
            if not practitioner or not customer:
                return

            purchased_qty = max(1, quantity)
            if deal.remaining_slots < purchased_qty:
                purchased_qty = deal.remaining_slots
            deal.remaining_slots -= purchased_qty

            unit_price = deal.price
            subtotal = unit_price * purchased_qty
            fee_amount = Decimal("0.00")
            total_amount = subtotal + fee_amount

            booking_number = f"BKG-{uuid.uuid4().hex[:10].upper()}"
            booking = Booking(
                booking_number=booking_number,
                deal_id=deal.id,
                practitioner_id=practitioner.id,
                customer_id=customer.id,
                customer_name=customer.name,
                customer_email=customer.email,
                customer_phone=None,
                avatar_url=None,
                quantity=purchased_qty,
                subtotal=subtotal,
                fee_amount=fee_amount,
                total_amount=total_amount,
                currency="USD",
                payment_status="paid",
                redemption_status="active",
                wallet_pass_id=None,
                qr_code=None,
            )
            self.session.add(booking)
            await self.session.flush()
            scope = EventScope(
                tenant_id=default_tenant(),
                practitioner_id=str(practitioner.id),
                actor_id=str(customer.id),
            )
            await emit_activity_event(
                self.session,
                scope=scope,
                entity_type="booking",
                entity_id=str(booking.id),
                event_type=ActivityEventType.BOOKING_CREATED,
                metadata={
                    "booking_id": str(booking.id),
                    "booking_number": booking.booking_number,
                    "attendee_name": customer.name,
                    "quantity": purchased_qty,
                    "amount": str(total_amount),
                },
            )

            wallet_pass = WalletPass(
                deal_id=deal_id,
                customer_id=customer_id,
                qr_code=uuid.uuid4().hex,
                status="issued",
                wallet_type="apple",
                source_checkout_session_id=checkout_session_id,
                booking_id=booking.id,
            )
            self.session.add(wallet_pass)
            await self.session.flush()
            await emit_activity_event(
                self.session,
                scope=scope,
                entity_type="wallet_pass",
                entity_id=str(wallet_pass.id),
                event_type=ActivityEventType.WALLET_GENERATED,
                metadata={"deal_id": str(deal.id), "booking_id": str(booking.id), "wallet_pass_id": str(wallet_pass.id)},
            )
            booking.wallet_pass_id = wallet_pass.id
            booking.qr_code = wallet_pass.qr_code
            await emit_activity_event(
                self.session,
                scope=scope,
                entity_type="booking",
                entity_id=str(booking.id),
                event_type=ActivityEventType.BOOKING_PAID,
                metadata={"booking_id": str(booking.id), "amount": str(booking.total_amount), "currency": booking.currency},
            )
            await self.session.commit()
        except ProgrammingError as exc:
            message = str(exc)
            if "does not exist" in message and "wallet_passes.booking_id" in message:
                await self.session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Database schema is out of date. Run API migrations (missing wallet_passes.booking_id).",
                ) from exc
            raise

        # Email should never block checkout finalization.
        MailService.send_booking_confirmation(
            customer_email=customer.email,
            customer_name=customer.name,
            deal_title=deal.title,
            starts_at=deal.start_time.isoformat(),
            location=deal.location,
            booking_number=booking.booking_number,
        )
        MailService.send_wallet_pass_delivery(
            customer_email=customer.email,
            customer_name=customer.name,
            deal_title=deal.title,
            qr_code=wallet_pass.qr_code,
        )

    async def create_checkout_session(self, payload: CheckoutSessionCreateRequest) -> CheckoutSessionCreateResponse:
        self._assert_configured()

        deal = await self.deal_repo.get(payload.deal_id)
        if not deal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
        if deal.status != "published":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Deal is not published")
        if deal.remaining_slots <= 0:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Deal is sold out")

        customer = await self._get_or_create_customer(payload.customer_email, payload.customer_name)

        if settings.payments_test_mode or settings.demo_checkout_mode:
            fake_session_id = f"test_cs_{uuid.uuid4().hex}"
            await self._finalize_paid_checkout(fake_session_id, deal.id, customer.id, payload.quantity)
            success_url = self._append_query(
                payload.success_url,
                {
                    "checkout": "success",
                    "session_id": fake_session_id,
                    "mode": "demo" if settings.demo_checkout_mode else "test",
                },
            )
            return CheckoutSessionCreateResponse(
                checkout_session_id=fake_session_id,
                checkout_url=success_url,
            )

        practitioner = await self.practitioner_repo.get(deal.practitioner_id)
        if not practitioner or not practitioner.stripe_account_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Practitioner Stripe account is not connected",
            )

        amount_cents = int(deal.price * 100)

        try:
            success_url = self._append_query(
                payload.success_url,
                {
                    "checkout": "success",
                    "session_id": "{CHECKOUT_SESSION_ID}",
                },
            )
            session = stripe.checkout.Session.create(
                mode="payment",
                success_url=success_url,
                cancel_url=payload.cancel_url,
                customer_email=customer.email,
                line_items=[
                    {
                        "quantity": max(1, payload.quantity),
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": amount_cents,
                            "product_data": {
                                "name": deal.title,
                                "description": deal.description,
                            },
                        },
                    }
                ],
                payment_intent_data={
                    "transfer_data": {
                        "destination": practitioner.stripe_account_id,
                    }
                },
                metadata={
                    "deal_id": str(deal.id),
                    "customer_id": str(customer.id),
                    "quantity": str(max(1, payload.quantity)),
                },
            )
        except stripe.error.StripeError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Stripe error: {exc.user_message or str(exc)}",
            )

        await self.session.commit()
        return CheckoutSessionCreateResponse(
            checkout_session_id=session.id,
            checkout_url=session.url,
        )

    async def get_checkout_result(self, checkout_session_id: str) -> CheckoutSessionResultResponse:
        wallet_pass = await self.wallet_repo.get_by_checkout_session_id(checkout_session_id)
        if not wallet_pass:
            return CheckoutSessionResultResponse(
                checkout_session_id=checkout_session_id,
                status="pending",
            )

        booking = await self.session.get(Booking, wallet_pass.booking_id) if wallet_pass.booking_id else None
        pass_url = wallet_pass.apple_wallet_url or wallet_pass.google_wallet_url

        return CheckoutSessionResultResponse(
            checkout_session_id=checkout_session_id,
            status="ready",
            wallet_pass_id=wallet_pass.id,
            booking_id=wallet_pass.booking_id,
            booking_number=booking.booking_number if booking else None,
            qr_code=wallet_pass.qr_code,
            apple_wallet_url=wallet_pass.apple_wallet_url,
            google_wallet_url=wallet_pass.google_wallet_url,
            pass_url=pass_url,
        )

    async def handle_webhook_event(self, payload: bytes, signature: str | None) -> dict[str, bool]:
        self._assert_configured()
        if settings.payments_test_mode:
            return {"received": True}
        if not settings.stripe_webhook_secret:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stripe webhook secret not configured",
            )
        if not signature:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Stripe signature")

        try:
            event = stripe.Webhook.construct_event(payload=payload, sig_header=signature, secret=settings.stripe_webhook_secret)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook payload") from exc
        except stripe.error.SignatureVerificationError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook signature") from exc

        if event["type"] != "checkout.session.completed":
            return {"received": True}

        data = event["data"]["object"]
        if data.get("payment_status") != "paid":
            return {"received": True}

        checkout_session_id = data.get("id")
        metadata = data.get("metadata") or {}
        deal_id = metadata.get("deal_id")
        customer_id = metadata.get("customer_id")

        if not checkout_session_id or not deal_id or not customer_id:
            return {"received": True}

        quantity = int(metadata.get("quantity", "1"))
        await self._finalize_paid_checkout(checkout_session_id, uuid.UUID(deal_id), uuid.UUID(customer_id), quantity)
        return {"received": True}
