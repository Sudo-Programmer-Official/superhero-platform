from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.types import AuthPrincipal
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

    async def start_onboarding(
        self, payload: StripeConnectStartRequest, principal: AuthPrincipal
    ) -> StripeConnectStartResponse:
        practitioner = await self.practitioner_repo.get_by_firebase_uid(principal.uid)
        if not practitioner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practitioner profile not found")

        account_id = practitioner.stripe_account_id or f"acct_{practitioner.id.hex[:16]}"
        practitioner.stripe_account_id = account_id

        # Placeholder onboarding URL contract; swap with real Stripe Account Link generation.
        onboarding_url = (
            f"https://connect.stripe.com/express/onboarding/{account_id}"
            f"?refresh_url={payload.refresh_url}&return_url={payload.return_url}"
        )

        await self.session.commit()
        return StripeConnectStartResponse(onboarding_url=onboarding_url, account_id=account_id)

    async def get_status(self, principal: AuthPrincipal) -> StripeConnectStatusResponse:
        practitioner = await self.practitioner_repo.get_by_firebase_uid(principal.uid)
        if not practitioner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practitioner profile not found")

        return StripeConnectStatusResponse(
            account_id=practitioner.stripe_account_id,
            onboarding_complete=bool(practitioner.stripe_onboarding_complete),
            payouts_enabled=bool(practitioner.stripe_onboarding_complete),
            charges_enabled=bool(practitioner.stripe_onboarding_complete),
        )
