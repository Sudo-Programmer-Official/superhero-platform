from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Booking, DealCard, Practitioner
from app.schemas.admin_ops import AdminDealRow, AdminPayoutRow, AdminPractitionerRow


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
