from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.types import AccessContext
from app.models import Booking, DealCard, WalletPass
from app.schemas.dashboard import DashboardMetricSummary, DashboardSummaryResponse, DashboardUpcomingItem


class DashboardService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_summary(self, access: AccessContext) -> DashboardSummaryResponse:
        booking_filters = []
        deal_filters = []
        wallet_filters = []

        if access.practitioner_id:
            booking_filters.append(Booking.practitioner_id == access.practitioner_id)
            deal_filters.append(DealCard.practitioner_id == access.practitioner_id)
            wallet_filters.append(DealCard.practitioner_id == access.practitioner_id)

        bookings_stmt: Select[tuple[int, Decimal | None]] = select(
            func.count(Booking.id),
            func.coalesce(func.sum(Booking.total_amount), 0),
        )
        if booking_filters:
            bookings_stmt = bookings_stmt.where(*booking_filters)
        bookings_count, revenue_sum = (await self.session.execute(bookings_stmt)).one()

        redemptions_stmt: Select[tuple[int]] = (
            select(func.count(WalletPass.id))
            .select_from(WalletPass)
            .join(DealCard, DealCard.id == WalletPass.deal_id)
            .where(WalletPass.status == "redeemed")
        )
        if wallet_filters:
            redemptions_stmt = redemptions_stmt.where(*wallet_filters)
        redemptions_count = (await self.session.execute(redemptions_stmt)).scalar_one()

        published_stmt: Select[tuple[int]] = select(func.count(DealCard.id)).where(DealCard.status == "published")
        if deal_filters:
            published_stmt = published_stmt.where(*deal_filters)
        published_count = (await self.session.execute(published_stmt)).scalar_one()

        conversion_rate = round((bookings_count / published_count) * 100, 1) if published_count > 0 else 0.0

        upcoming_stmt = (
            select(DealCard)
            .where(DealCard.status == "published", DealCard.start_time >= datetime.now(UTC))
            .order_by(DealCard.start_time.asc())
            .limit(6)
        )
        if deal_filters:
            upcoming_stmt = upcoming_stmt.where(*deal_filters)
        upcoming_deals = list((await self.session.scalars(upcoming_stmt)).all())
        upcoming = [
            DashboardUpcomingItem(
                id=str(deal.id),
                title=deal.title,
                image=deal.image,
                starts_at=deal.start_time,
                location=deal.location,
                seats_sold=max(0, deal.capacity - deal.remaining_slots),
                capacity=deal.capacity,
            )
            for deal in upcoming_deals
        ]

        return DashboardSummaryResponse(
            metrics=DashboardMetricSummary(
                total_bookings=int(bookings_count or 0),
                revenue=float(revenue_sum or 0),
                redemptions=int(redemptions_count or 0),
                conversion_rate=conversion_rate,
            ),
            upcoming=upcoming,
        )

