from fastapi import APIRouter

from .routes.activity_events import router as activity_events_router
from .routes.bookings import router as bookings_router
from .routes.deal_cards import router as deal_cards_router
from .routes.me import router as me_router
from .routes.payments import router as payments_router
from .routes.practitioners import router as practitioners_router
from .routes.storage import router as storage_router
from .routes.stripe_connect import router as stripe_connect_router
from .routes.super_admin import router as super_admin_router
from .routes.wallet_passes import router as wallet_passes_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(me_router)
api_router.include_router(practitioners_router)
api_router.include_router(deal_cards_router)
api_router.include_router(bookings_router)
api_router.include_router(activity_events_router)
api_router.include_router(payments_router)
api_router.include_router(storage_router)
api_router.include_router(wallet_passes_router)
api_router.include_router(stripe_connect_router)
api_router.include_router(super_admin_router)
