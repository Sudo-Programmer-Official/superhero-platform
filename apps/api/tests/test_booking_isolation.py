from __future__ import annotations

import asyncio
from uuid import uuid4

from app.auth.types import AccessContext, AuthPrincipal
from app.services.booking_service import BookingService


def _access(practitioner_id=None, role: str = "practitioner") -> AccessContext:
    return AccessContext(
        principal=AuthPrincipal(uid="test-uid", email="test@example.com", role=role),
        tenant_id="superhero_platform",
        practitioner_id=practitioner_id,
        role=role,
    )


def test_booking_service_scopes_by_practitioner_id(monkeypatch) -> None:
    practitioner_id = uuid4()
    called = {"by_practitioner": False, "all": False}

    async def fake_by_practitioner(value):
        called["by_practitioner"] = True
        assert value == practitioner_id
        return ["alpha"]

    async def fake_all():
        called["all"] = True
        raise AssertionError("list_all should not be used when practitioner_id exists")

    service = BookingService(session=object())
    monkeypatch.setattr(service.repo, "list_by_practitioner", fake_by_practitioner)
    monkeypatch.setattr(service.repo, "list_all", fake_all)

    result = asyncio.run(service.list_bookings(_access(practitioner_id=practitioner_id)))

    assert result == ["alpha"]
    assert called == {"by_practitioner": True, "all": False}


def test_booking_service_uses_global_list_for_admin_without_practitioner(monkeypatch) -> None:
    called = {"by_practitioner": False, "all": False}

    async def fake_by_practitioner(_value):
        called["by_practitioner"] = True
        raise AssertionError("list_by_practitioner should not be used without practitioner_id")

    async def fake_all():
        called["all"] = True
        return ["alpha"]

    service = BookingService(session=object())
    monkeypatch.setattr(service.repo, "list_by_practitioner", fake_by_practitioner)
    monkeypatch.setattr(service.repo, "list_all", fake_all)

    result = asyncio.run(service.list_bookings(_access(role="admin")))

    assert result == ["alpha"]
    assert called == {"by_practitioner": False, "all": True}
