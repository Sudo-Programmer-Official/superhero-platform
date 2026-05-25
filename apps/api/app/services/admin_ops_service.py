from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import case, cast, func, or_, select, String
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ActivityEvent, Booking, DealCard, Practitioner, WalletPass
from app.schemas.admin_ops import (
    AdminBookingRow,
    AdminDealRow,
    AdminPayoutRow,
    AdminPractitionerRow,
    AdminRedemptionRow,
    AdminTimelineEventRow,
    AdminWalletPassRow,
)


class AdminOpsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_practitioners(self, query: str | None = None) -> list[AdminPractitionerRow]:
        stmt = select(Practitioner).order_by(Practitioner.created_at.desc())
        if query:
            pattern = f"%{query.strip()}%"
            stmt = stmt.where(or_(Practitioner.name.ilike(pattern), Practitioner.slug.ilike(pattern)))

        practitioners = (await self.session.execute(stmt)).scalars().all()
        rows: list[AdminPractitionerRow] = []
        for p in practitioners:
            stripe_state = "connected" if p.stripe_onboarding_complete else "onboarding" if p.stripe_account_id else "missing"
            payout_status = "connected" if p.stripe_onboarding_complete else "pending" if p.stripe_account_id else "restricted"
            verification_state = p.verification_state if p.verification_state in {"verified", "pending", "flagged"} else "pending"
            health = "healthy" if p.is_public and stripe_state == "connected" else "watch" if p.is_public else "critical"
            rows.append(
                AdminPractitionerRow(
                    id=p.id,
                    name=p.name,
                    slug=p.slug,
                    subscription_status="active" if p.is_public else "grace",
                    payout_status=payout_status,
                    stripe_state=stripe_state,
                    verification_state=verification_state,
                    health=health,
                    is_public=p.is_public,
                    created_at=p.created_at,
                )
            )
        return rows

    async def apply_practitioner_action(self, practitioner_id: UUID, action: str) -> AdminPractitionerRow:
        p = await self.session.get(Practitioner, practitioner_id)
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practitioner not found")

        if action == "suspend":
            p.is_public = False
            branding = dict(p.branding or {})
            branding["account_state"] = "suspended"
            p.branding = branding
        elif action == "activate":
            p.is_public = True
            branding = dict(p.branding or {})
            branding["account_state"] = "active"
            p.branding = branding
        elif action == "reset_onboarding":
            p.stripe_onboarding_complete = False
        elif action in {"impersonate", "grant_credits", "resend_verification"}:
            pass
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported practitioner action")

        await self.session.commit()
        rows = await self.list_practitioners()
        for row in rows:
            if row.id == p.id:
                return row
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to reload practitioner")

    async def list_deals(self, query: str | None = None, deal_status: str | None = None) -> list[AdminDealRow]:
        revenue_expr = func.coalesce(func.sum(case((Booking.payment_status == "paid", Booking.total_amount), else_=0)), 0)
        bookings_expr = func.count(Booking.id)
        stmt = (
            select(
                DealCard.id,
                DealCard.title,
                DealCard.slug,
                DealCard.practitioner_id,
                Practitioner.name.label("practitioner_name"),
                DealCard.status,
                DealCard.start_time,
                DealCard.created_at,
                revenue_expr.label("revenue"),
                bookings_expr.label("bookings_count"),
            )
            .join(Practitioner, Practitioner.id == DealCard.practitioner_id)
            .outerjoin(Booking, Booking.deal_id == DealCard.id)
            .group_by(
                DealCard.id,
                DealCard.title,
                DealCard.slug,
                DealCard.practitioner_id,
                Practitioner.name,
                DealCard.status,
                DealCard.start_time,
                DealCard.created_at,
            )
            .order_by(DealCard.created_at.desc())
        )
        if query:
            pattern = f"%{query.strip()}%"
            stmt = stmt.where(or_(DealCard.title.ilike(pattern), DealCard.slug.ilike(pattern), Practitioner.name.ilike(pattern)))
        if deal_status and deal_status != "all":
            normalized = "canceled" if deal_status == "archived" else deal_status
            stmt = stmt.where(DealCard.status == normalized)

        rows = (await self.session.execute(stmt)).all()
        return [
            AdminDealRow(
                id=row.id,
                title=row.title,
                slug=row.slug,
                practitioner_id=row.practitioner_id,
                practitioner_name=row.practitioner_name,
                status="archived" if row.status == "canceled" else row.status,
                moderation_state="flagged" if row.status == "canceled" else "clean",
                revenue=Decimal(row.revenue or 0),
                bookings_count=int(row.bookings_count or 0),
                start_time=row.start_time,
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def apply_deal_action(self, deal_id: UUID, action: str) -> AdminDealRow:
        deal = await self.session.get(DealCard, deal_id)
        if not deal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")

        if action == "archive":
            deal.status = "canceled"
            deal.share_link = None
        elif action == "unpublish":
            deal.status = "draft"
            deal.share_link = None
        elif action == "feature":
            pass
        elif action == "moderate":
            if deal.status == "published":
                deal.status = "draft"
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported deal action")

        await self.session.commit()
        rows = await self.list_deals()
        for row in rows:
            if row.id == deal.id:
                return row
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to reload deal")

    async def list_payouts(self, query: str | None = None, payout_status: str | None = None) -> list[AdminPayoutRow]:
        amount_expr = func.coalesce(func.sum(Booking.total_amount - Booking.fee_amount), 0)
        tx_count_expr = func.count(Booking.id)
        pending_count_expr = func.sum(case((Booking.payment_status == "pending", 1), else_=0))
        failed_count_expr = func.sum(case((Booking.payment_status == "failed", 1), else_=0))
        paid_count_expr = func.sum(case((Booking.payment_status == "paid", 1), else_=0))
        last_created_expr = func.max(Booking.created_at)
        stmt = (
            select(
                Practitioner.id.label("practitioner_id"),
                Practitioner.name.label("creator"),
                amount_expr.label("amount"),
                tx_count_expr.label("transaction_count"),
                pending_count_expr.label("pending_count"),
                failed_count_expr.label("failed_count"),
                paid_count_expr.label("paid_count"),
                last_created_expr.label("last_created_at"),
            )
            .join(Booking, Booking.practitioner_id == Practitioner.id)
            .group_by(Practitioner.id, Practitioner.name)
            .order_by(last_created_expr.desc())
        )
        if query:
            pattern = f"%{query.strip()}%"
            stmt = stmt.where(or_(Practitioner.name.ilike(pattern), Practitioner.slug.ilike(pattern)))

        agg_rows = (await self.session.execute(stmt)).all()
        rows: list[AdminPayoutRow] = []
        for row in agg_rows:
            pending_count = int(row.pending_count or 0)
            failed_count = int(row.failed_count or 0)
            paid_count = int(row.paid_count or 0)
            payout_state = "pending" if pending_count > 0 else "failed" if failed_count > 0 else "paid" if paid_count > 0 else "processing"
            transfer_state = "queued" if pending_count > 0 else "error" if failed_count > 0 else "completed"
            if payout_status and payout_status != "all" and payout_state != payout_status:
                continue
            rows.append(
                AdminPayoutRow(
                    id=f"po-{row.practitioner_id}",
                    practitioner_id=row.practitioner_id,
                    creator=row.creator,
                    amount=Decimal(row.amount or 0),
                    status=payout_state,
                    transfer_state=transfer_state,
                    transaction_count=int(row.transaction_count or 0),
                    processing_date=row.last_created_at,
                    payout_date=datetime.now(timezone.utc) if payout_state == "paid" else None,
                )
            )
        return rows

    async def apply_payout_action(self, practitioner_id: UUID, action: str) -> AdminPayoutRow:
        bookings = (
            await self.session.execute(select(Booking).where(Booking.practitioner_id == practitioner_id).order_by(Booking.created_at.desc()))
        ).scalars().all()
        if not bookings:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No payout bookings found")

        if action == "mark_paid":
            for booking in bookings:
                if booking.payment_status in {"pending", "processing"}:
                    booking.payment_status = "paid"
        elif action == "retry":
            for booking in bookings:
                if booking.payment_status == "failed":
                    booking.payment_status = "pending"
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported payout action")

        await self.session.commit()
        rows = await self.list_payouts()
        for row in rows:
            if row.practitioner_id == practitioner_id:
                return row
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to reload payout row")

    async def list_bookings(self, query: str | None = None, payment_status: str | None = None) -> list[AdminBookingRow]:
        stmt = (
            select(
                Booking.id,
                Booking.booking_number,
                DealCard.title.label("deal_title"),
                Practitioner.name.label("practitioner_name"),
                Booking.customer_name,
                Booking.customer_email,
                Booking.quantity,
                Booking.total_amount,
                Booking.currency,
                Booking.payment_status,
                Booking.redemption_status,
                Booking.wallet_pass_id,
                Booking.created_at,
            )
            .join(DealCard, DealCard.id == Booking.deal_id)
            .join(Practitioner, Practitioner.id == Booking.practitioner_id)
            .order_by(Booking.created_at.desc())
        )
        if query:
            pattern = f"%{query.strip()}%"
            stmt = stmt.where(
                or_(
                    Booking.booking_number.ilike(pattern),
                    Booking.customer_email.ilike(pattern),
                    Booking.customer_name.ilike(pattern),
                    DealCard.title.ilike(pattern),
                    Practitioner.name.ilike(pattern),
                )
            )
        if payment_status and payment_status != "all":
            stmt = stmt.where(Booking.payment_status == payment_status)

        rows = (await self.session.execute(stmt)).all()
        return [
            AdminBookingRow(
                id=row.id,
                booking_number=row.booking_number,
                deal_title=row.deal_title,
                practitioner_name=row.practitioner_name,
                customer_name=row.customer_name,
                customer_email=row.customer_email,
                quantity=int(row.quantity),
                total_amount=Decimal(row.total_amount or 0),
                currency=row.currency,
                payment_status=row.payment_status,
                redemption_status=row.redemption_status,
                wallet_pass_id=row.wallet_pass_id,
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def list_wallet_passes(self, query: str | None = None, pass_status: str | None = None) -> list[AdminWalletPassRow]:
        stmt = (
            select(
                WalletPass.id,
                DealCard.title.label("deal_title"),
                Practitioner.name.label("practitioner_name"),
                Booking.customer_email.label("attendee_email"),
                Booking.booking_number.label("booking_number"),
                WalletPass.status.label("pass_status"),
                WalletPass.wallet_type,
                WalletPass.source_checkout_session_id,
                WalletPass.qr_code,
                WalletPass.created_at,
            )
            .join(DealCard, DealCard.id == WalletPass.deal_id)
            .join(Practitioner, Practitioner.id == DealCard.practitioner_id)
            .outerjoin(Booking, Booking.id == WalletPass.booking_id)
            .order_by(WalletPass.created_at.desc())
        )
        if query:
            pattern = f"%{query.strip()}%"
            stmt = stmt.where(
                or_(
                    DealCard.title.ilike(pattern),
                    Practitioner.name.ilike(pattern),
                    Booking.customer_email.ilike(pattern),
                    Booking.booking_number.ilike(pattern),
                    WalletPass.qr_code.ilike(pattern),
                )
            )
        if pass_status and pass_status != "all":
            stmt = stmt.where(WalletPass.status == pass_status)

        rows = (await self.session.execute(stmt)).all()
        return [
            AdminWalletPassRow(
                id=row.id,
                deal_title=row.deal_title,
                practitioner_name=row.practitioner_name,
                attendee_email=row.attendee_email,
                booking_number=row.booking_number,
                pass_status=row.pass_status,
                redemption_status="redeemed" if row.pass_status == "redeemed" else row.pass_status if row.pass_status in {"expired", "revoked"} else "active",
                wallet_type=row.wallet_type,
                source_checkout_session_id=row.source_checkout_session_id,
                qr_code=row.qr_code,
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def list_redemptions(self, query: str | None = None, window: str | None = None) -> list[AdminRedemptionRow]:
        reason_expr = cast(ActivityEvent.event_metadata["reason"].astext, String)
        duplicate_expr = func.sum(case((reason_expr == "already_redeemed", 1), else_=0))
        invalid_expr = func.sum(case((reason_expr == "not_found", 1), else_=0))
        success_expr = func.sum(case((ActivityEvent.event_type == "redemption.success", 1), else_=0))
        failed_expr = func.sum(case((ActivityEvent.event_type == "redemption.failed", 1), else_=0))
        last_event_expr = func.max(ActivityEvent.created_at)

        stmt = (
            select(
                ActivityEvent.entity_id.label("wallet_pass_id"),
                DealCard.title.label("deal_title"),
                Practitioner.name.label("practitioner_name"),
                Booking.customer_email.label("attendee_email"),
                success_expr.label("success_count"),
                failed_expr.label("failed_count"),
                duplicate_expr.label("duplicate_attempts"),
                invalid_expr.label("invalid_attempts"),
                last_event_expr.label("last_event_at"),
            )
            .outerjoin(WalletPass, cast(WalletPass.id, String) == ActivityEvent.entity_id)
            .outerjoin(DealCard, DealCard.id == WalletPass.deal_id)
            .outerjoin(Practitioner, Practitioner.id == DealCard.practitioner_id)
            .outerjoin(Booking, Booking.id == WalletPass.booking_id)
            .where(ActivityEvent.entity_type == "redemption")
            .where(ActivityEvent.event_type.in_(["redemption.success", "redemption.failed"]))
            .group_by(ActivityEvent.entity_id, DealCard.title, Practitioner.name, Booking.customer_email)
            .order_by(last_event_expr.desc())
        )
        if window and window != "all":
            now = datetime.now(timezone.utc)
            cutoff: datetime | None = None
            if window == "24h":
                cutoff = now - timedelta(hours=24)
            elif window == "7d":
                cutoff = now - timedelta(days=7)
            elif window == "30d":
                cutoff = now - timedelta(days=30)
            if cutoff is not None:
                stmt = stmt.where(ActivityEvent.created_at >= cutoff)
        if query:
            pattern = f"%{query.strip()}%"
            stmt = stmt.where(
                or_(
                    ActivityEvent.entity_id.ilike(pattern),
                    Booking.customer_email.ilike(pattern),
                    DealCard.title.ilike(pattern),
                    Practitioner.name.ilike(pattern),
                )
            )

        rows = (await self.session.execute(stmt)).all()
        data: list[AdminRedemptionRow] = []
        for row in rows:
            duplicate_attempts = int(row.duplicate_attempts or 0)
            invalid_attempts = int(row.invalid_attempts or 0)
            failed_count = int(row.failed_count or 0)
            if invalid_attempts > 0:
                risk = "critical"
            elif duplicate_attempts > 0:
                risk = "watch"
            elif failed_count > 0:
                risk = "elevated"
            else:
                risk = "healthy"

            data.append(
                AdminRedemptionRow(
                    wallet_pass_id=row.wallet_pass_id,
                    deal_title=row.deal_title,
                    practitioner_name=row.practitioner_name,
                    attendee_email=row.attendee_email,
                    success_count=int(row.success_count or 0),
                    failed_count=failed_count,
                    duplicate_attempts=duplicate_attempts,
                    invalid_attempts=invalid_attempts,
                    last_event_at=row.last_event_at,
                    risk_level=risk,
                )
            )
        return data

    async def list_timeline(
        self,
        *,
        entity_type: str,
        entity_id: str,
        limit: int = 80,
    ) -> list[AdminTimelineEventRow]:
        entity_pairs: list[tuple[str, str]] = [(entity_type, entity_id)]

        if entity_type == "booking":
            try:
                booking_uuid = UUID(entity_id)
            except ValueError:
                booking_uuid = None
            booking = await self.session.get(Booking, booking_uuid) if booking_uuid else None
            if booking and booking.wallet_pass_id:
                pass_id = str(booking.wallet_pass_id)
                entity_pairs.append(("wallet_pass", pass_id))
                entity_pairs.append(("redemption", pass_id))
        elif entity_type == "wallet_pass":
            try:
                wallet_uuid = UUID(entity_id)
            except ValueError:
                wallet_uuid = None
            wallet_pass = await self.session.get(WalletPass, wallet_uuid) if wallet_uuid else None
            if wallet_pass and wallet_pass.booking_id:
                entity_pairs.append(("booking", str(wallet_pass.booking_id)))
            entity_pairs.append(("redemption", entity_id))
        elif entity_type == "redemption":
            entity_pairs.append(("wallet_pass", entity_id))

        filters = [
            (ActivityEvent.entity_type == pair_type) & (ActivityEvent.entity_id == pair_id)
            for pair_type, pair_id in entity_pairs
        ]
        stmt = (
            select(ActivityEvent)
            .where(or_(*filters))
            .order_by(ActivityEvent.created_at.desc(), ActivityEvent.id.desc())
            .limit(max(1, min(limit, 200)))
        )
        rows = (await self.session.execute(stmt)).scalars().all()
        return [
            AdminTimelineEventRow(
                id=row.id,
                entity_type=row.entity_type,
                entity_id=row.entity_id,
                event_type=row.event_type,
                metadata=row.event_metadata or {},
                created_at=row.created_at,
            )
            for row in rows
        ]
