from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.schemas.payment import CheckoutSessionCreateRequest, CheckoutSessionCreateResponse, CheckoutSessionResultResponse
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/checkout-session", response_model=CheckoutSessionCreateResponse)
async def create_checkout_session(
    payload: CheckoutSessionCreateRequest,
    session: AsyncSession = Depends(get_db_session),
):
    return await PaymentService(session).create_checkout_session(payload)


@router.post("/webhook")
async def payments_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="stripe-signature"),
    session: AsyncSession = Depends(get_db_session),
):
    payload = await request.body()
    return await PaymentService(session).handle_webhook_event(payload, stripe_signature)


@router.get("/checkout-result", response_model=CheckoutSessionResultResponse)
async def checkout_result(
    session_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    return await PaymentService(session).get_checkout_result(session_id)
