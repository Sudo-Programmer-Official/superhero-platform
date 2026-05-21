from __future__ import annotations

import stripe
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.types import AuthPrincipal
from app.config import settings
from app.repositories.practitioner_repository import PractitionerRepository
from app.schemas.stripe_connect import (
    StripeConnectStartRequest,
    StripeConnectStartResponse,
    StripeConnectStatusResponse,
)


class StripeConnectService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.practitioner_repo = PractitionerRepository(session)
        stripe.api_key = settings.stripe_secret_key

    def _assert_configured(self) -> None:
        if not settings.stripe_secret_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stripe secret key not configured",
            )

    async def _ensure_connected_account(self, principal: AuthPrincipal):
        practitioner = await self.practitioner_repo.get_by_firebase_uid(principal.uid)
        if not practitioner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practitioner profile not found")

        if practitioner.stripe_account_id:
            return practitioner, practitioner.stripe_account_id

        try:
            account = stripe.Account.create(
                type="express",
                country=settings.stripe_country,
                email=principal.email,
                metadata={
                    "practitioner_id": str(practitioner.id),
                    "firebase_uid": principal.uid,
                },
            )
        except stripe.error.StripeError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Stripe error: {exc.user_message or str(exc)}")

        practitioner.stripe_account_id = account.id
        practitioner.stripe_onboarding_complete = bool(getattr(account, "details_submitted", False))
        await self.session.commit()
        return practitioner, account.id

    async def start_onboarding(
        self, payload: StripeConnectStartRequest, principal: AuthPrincipal
    ) -> StripeConnectStartResponse:
        self._assert_configured()
        _, account_id = await self._ensure_connected_account(principal)

        try:
            link = stripe.AccountLink.create(
                account=account_id,
                type="account_onboarding",
                refresh_url=payload.refresh_url,
                return_url=payload.return_url,
            )
        except stripe.error.StripeError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Stripe error: {exc.user_message or str(exc)}")

        return StripeConnectStartResponse(onboarding_url=link.url, account_id=account_id)

    async def get_status(self, principal: AuthPrincipal) -> StripeConnectStatusResponse:
        self._assert_configured()
        practitioner = await self.practitioner_repo.get_by_firebase_uid(principal.uid)
        if not practitioner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practitioner profile not found")

        if not practitioner.stripe_account_id:
            return StripeConnectStatusResponse(
                account_id=None,
                onboarding_complete=False,
                payouts_enabled=False,
                charges_enabled=False,
            )

        try:
            account = stripe.Account.retrieve(practitioner.stripe_account_id)
        except stripe.error.StripeError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Stripe error: {exc.user_message or str(exc)}")

        practitioner.stripe_onboarding_complete = bool(getattr(account, "details_submitted", False))
        await self.session.commit()

        return StripeConnectStatusResponse(
            account_id=practitioner.stripe_account_id,
            onboarding_complete=bool(getattr(account, "details_submitted", False)),
            payouts_enabled=bool(getattr(account, "payouts_enabled", False)),
            charges_enabled=bool(getattr(account, "charges_enabled", False)),
        )

    async def handle_webhook_event(self, payload: bytes, signature: str | None) -> dict[str, bool]:
        self._assert_configured()
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

        event_type = event["type"]
        data_object = event["data"]["object"]

        if event_type in {"account.updated", "account.application.deauthorized"}:
            account_id = data_object.get("id")
            if account_id:
                practitioner = await self.practitioner_repo.get_by_stripe_account_id(account_id)
                if practitioner:
                    practitioner.stripe_onboarding_complete = bool(data_object.get("details_submitted", False))
                    if event_type == "account.application.deauthorized":
                        practitioner.stripe_onboarding_complete = False
                    await self.session.commit()

        return {"received": True}
