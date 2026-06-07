from __future__ import annotations

import asyncio
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException

from app.auth.types import AccessContext, AuthPrincipal
from app.api.v1.routes.deal_cards import list_deal_cards
from app.services.deal_card_service import DealCardService


def _override_access_context(practitioner_id=None, role: str = "practitioner") -> AccessContext:
    return AccessContext(
        principal=AuthPrincipal(uid="test-uid", email="test@example.com", role=role),
        tenant_id="superhero_platform",
        practitioner_id=practitioner_id,
        role=role,
    )


def test_deal_cards_route_passes_access_context(monkeypatch) -> None:
    seen = {}

    async def fake_list(self: DealCardService, access: AccessContext):
        seen["role"] = access.role
        seen["practitioner_id"] = access.practitioner_id
        return []

    monkeypatch.setattr(DealCardService, "list_deals", fake_list)

    practitioner_id = uuid4()
    access = _override_access_context(practitioner_id=practitioner_id)
    result = asyncio.run(list_deal_cards(access=access, session=object()))

    assert result == []
    assert seen == {"role": "practitioner", "practitioner_id": practitioner_id}


def test_deal_cards_service_scopes_practitioner_list(monkeypatch) -> None:
    practitioner_id = uuid4()
    called = {"by_practitioner": False, "all": False}

    async def fake_list_by_practitioner(value):
        called["by_practitioner"] = True
        assert value == practitioner_id
        return ["alpha"]

    async def fake_list_all():
        called["all"] = True
        raise AssertionError("list_all should not be used for practitioner access")

    service = DealCardService(session=object())
    monkeypatch.setattr(service.repo, "list_by_practitioner", fake_list_by_practitioner)
    monkeypatch.setattr(service.repo, "list_all", fake_list_all)

    access = _override_access_context(practitioner_id=practitioner_id)
    result = asyncio.run(service.list_deals(access))

    assert result == ["alpha"]
    assert called == {"by_practitioner": True, "all": False}


def test_public_deal_list_scopes_to_practitioner_slug(monkeypatch) -> None:
    practitioner_id = uuid4()
    public_practitioner = SimpleNamespace(id=practitioner_id, is_public=True)
    deal = SimpleNamespace(id=uuid4(), practitioner_id=practitioner_id, status="published")
    called = {"slug": None, "practitioner": None}

    async def fake_get_by_slug(slug: str):
        called["slug"] = slug
        return public_practitioner

    async def fake_list_by_practitioner(value):
        called["practitioner"] = value
        assert value == practitioner_id
        return [deal]

    service = DealCardService(session=object())
    monkeypatch.setattr(service.practitioner_repo, "get_by_slug", fake_get_by_slug)
    monkeypatch.setattr(service.repo, "list_by_practitioner", fake_list_by_practitioner)

    result = asyncio.run(service.list_public_deals_for_practitioner("summer-spa"))

    assert result == [deal]
    assert called == {"slug": "summer-spa", "practitioner": practitioner_id}


def test_public_deal_requires_matching_practitioner(monkeypatch) -> None:
    owner_id = uuid4()
    other_owner_id = uuid4()
    public_practitioner = SimpleNamespace(id=owner_id, is_public=True)
    foreign_deal = SimpleNamespace(id=uuid4(), practitioner_id=other_owner_id, status="published")

    async def fake_get_by_slug(slug: str):
        return public_practitioner

    async def fake_get_public(slug: str):
        assert slug == "alpha"
        return foreign_deal

    service = DealCardService(session=object())
    monkeypatch.setattr(service.practitioner_repo, "get_by_slug", fake_get_by_slug)
    monkeypatch.setattr(service.repo, "get_by_slug", fake_get_public)

    try:
        asyncio.run(service.get_public_deal("summer-spa", "alpha"))
        raise AssertionError("Expected HTTPException")
    except HTTPException as exc:
        assert exc.status_code == 404
