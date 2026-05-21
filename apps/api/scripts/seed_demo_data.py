from __future__ import annotations

import asyncio
import os
import sys
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select, text

# Allow running as: python3 scripts/seed_demo_data.py from apps/api
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.db import SessionLocal
from app.config import settings
from app.models import Customer, DealCard, Practitioner, WalletPass
from app.utils.slug import slugify


async def _ensure_search_path(session) -> None:
    await session.execute(text(f'SET search_path TO "{settings.db_schema}"'))


async def _get_or_create_practitioner(name: str, bio: str, location: str) -> Practitioner:
    async with SessionLocal() as session:
        await _ensure_search_path(session)
        slug = slugify(name)
        existing = await session.scalar(select(Practitioner).where(Practitioner.slug == slug))
        if existing:
            return existing

        model = Practitioner(
            name=name,
            slug=slug,
            bio=bio,
            location=location,
            is_public=True,
        )
        session.add(model)
        await session.commit()
        await session.refresh(model)
        return model


async def _get_or_create_customer(email: str, name: str) -> Customer:
    async with SessionLocal() as session:
        await _ensure_search_path(session)
        existing = await session.scalar(select(Customer).where(Customer.email == email))
        if existing:
            return existing
        customer = Customer(email=email, name=name)
        session.add(customer)
        await session.commit()
        await session.refresh(customer)
        return customer


async def _create_demo_deals(practitioner: Practitioner, prefix: str) -> list[DealCard]:
    async with SessionLocal() as session:
        await _ensure_search_path(session)
        existing = await session.scalars(select(DealCard).where(DealCard.practitioner_id == practitioner.id))
        existing_list = list(existing)
        if existing_list:
            return existing_list

        now = datetime.now(UTC)
        deals = [
            DealCard(
                practitioner_id=practitioner.id,
                title=f"{prefix} Breathwork Journey",
                slug=f"{slugify(prefix)}-breathwork-journey",
                description="Guided breathwork for stress relief and grounding.",
                image="https://images.unsplash.com/photo-1506126613408-eca07ce68773",
                price=Decimal("39.00"),
                capacity=20,
                remaining_slots=20,
                location=practitioner.location or "Studio",
                start_time=now + timedelta(days=3),
                end_time=now + timedelta(days=3, hours=2),
                expiration_time=now + timedelta(days=3),
                cta_text="Reserve spot",
                booking_url="https://calendly.com",
                status="published",
                share_link=f"/openmat/{practitioner.slug}/{slugify(prefix)}-breathwork-journey",
                wallet_enabled=True,
            ),
            DealCard(
                practitioner_id=practitioner.id,
                title=f"{prefix} Membership Intro",
                slug=f"{slugify(prefix)}-membership-intro",
                description="Intro offer for monthly wellness membership.",
                image="https://images.unsplash.com/photo-1545205597-3d9d02c29597",
                price=Decimal("59.00"),
                capacity=30,
                remaining_slots=30,
                location=practitioner.location or "Studio",
                start_time=now + timedelta(days=10),
                end_time=now + timedelta(days=10, hours=1),
                expiration_time=now + timedelta(days=10),
                cta_text="Join now",
                booking_url="https://calendly.com",
                status="draft",
                share_link=None,
                wallet_enabled=True,
            ),
        ]
        session.add_all(deals)
        await session.commit()
        result = await session.scalars(select(DealCard).where(DealCard.practitioner_id == practitioner.id))
        return list(result)


async def _create_demo_wallet_pass(deal: DealCard, customer: Customer) -> None:
    async with SessionLocal() as session:
        await _ensure_search_path(session)
        existing = await session.scalar(
            select(WalletPass).where(WalletPass.deal_id == deal.id, WalletPass.customer_id == customer.id)
        )
        if existing:
            return
        wallet_pass = WalletPass(
            deal_id=deal.id,
            customer_id=customer.id,
            qr_code=f"demo-{deal.slug}-{customer.id.hex[:8]}",
            status="issued",
            wallet_type="apple",
        )
        session.add(wallet_pass)
        await session.commit()


async def main() -> None:
    marla = await _get_or_create_practitioner("Marla Therapist", "Trauma-informed therapist and breath coach.", "Austin")
    nora = await _get_or_create_practitioner("Nora Yoga", "Vinyasa and restorative yoga facilitator.", "Denver")
    kai = await _get_or_create_practitioner("Kai Wellness", "Mobility and recovery specialist.", "Chicago")

    marla_deals = await _create_demo_deals(marla, "Marla")
    await _create_demo_deals(nora, "Nora")
    await _create_demo_deals(kai, "Kai")

    customer = await _get_or_create_customer("demo.customer@example.com", "Demo Customer")
    await _create_demo_wallet_pass(marla_deals[0], customer)

    print("Demo data seeded.")


if __name__ == "__main__":
    asyncio.run(main())
