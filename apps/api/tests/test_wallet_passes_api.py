from __future__ import annotations

from uuid import uuid4

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.auth.dependencies import get_access_context
from app.auth.types import AccessContext, AuthPrincipal
from app.db import get_db_session
from app.main import app
from app.services.wallet_pass_service import WalletPassService


def _override_access_context(role: str = "practitioner") -> AccessContext:
    return AccessContext(
        principal=AuthPrincipal(uid="test-uid", email="test@example.com", role=role),
        tenant_id="superhero_platform",
        practitioner_id=uuid4(),
        role=role,
    )


async def _override_db_session():
    yield None


def test_wallet_passes_list_empty_state_returns_200_json(monkeypatch) -> None:
    async def fake_list(self: WalletPassService, access: AccessContext):
        assert access.role == "practitioner"
        return []

    monkeypatch.setattr(WalletPassService, "list_wallet_passes", fake_list)
    app.dependency_overrides[get_access_context] = lambda: _override_access_context("practitioner")
    app.dependency_overrides[get_db_session] = _override_db_session

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/wallet-passes")
        assert response.status_code == 200
        assert response.json() == []
    finally:
        app.dependency_overrides.clear()


def test_wallet_passes_list_returns_canonical_payload_shape(monkeypatch) -> None:
    wallet_id = str(uuid4())
    booking_id = str(uuid4())
    deal_id = str(uuid4())
    owner_id = str(uuid4())

    async def fake_list(self: WalletPassService, access: AccessContext):
        assert access.role == "admin"
        return [
            {
                "id": wallet_id,
                "booking_id": booking_id,
                "deal_id": deal_id,
                "owner_id": owner_id,
                "customer_id": owner_id,
                "qr_code": "qr-123",
                "pass_status": "active",
                "status": "active",
                "redemption_status": "active",
                "expires_at": None,
                "redeemed_at": None,
                "source_checkout_session_id": None,
                "wallet_provider": "apple",
                "wallet_type": "apple",
                "apple_wallet_url": None,
                "google_wallet_url": None,
                "created_at": "2026-05-23T10:00:00Z",
            }
        ]

    monkeypatch.setattr(WalletPassService, "list_wallet_passes", fake_list)
    app.dependency_overrides[get_access_context] = lambda: _override_access_context("admin")
    app.dependency_overrides[get_db_session] = _override_db_session

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/wallet-passes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == wallet_id
        assert data[0]["booking_id"] == booking_id
        assert data[0]["deal_id"] == deal_id
        assert data[0]["owner_id"] == owner_id
        assert data[0]["pass_status"] == "active"
        assert data[0]["redemption_status"] == "active"
    finally:
        app.dependency_overrides.clear()


def test_wallet_passes_redeem_not_found_returns_typed_error(monkeypatch) -> None:
    async def fake_redeem(self: WalletPassService, qr_code: str, principal: AuthPrincipal):
        raise HTTPException(status_code=404, detail="Wallet pass not found")

    monkeypatch.setattr(WalletPassService, "redeem_by_qr", fake_redeem)
    app.dependency_overrides[get_access_context] = lambda: _override_access_context("practitioner")
    app.dependency_overrides[get_db_session] = _override_db_session

    try:
        with TestClient(app) as client:
            response = client.post("/api/v1/wallet-passes/redeem", json={"qr_code": "missing-code"})
        assert response.status_code == 404
        body = response.json()
        assert body["error"]["code"] == "http_error"
        assert body["error"]["message"] == "Wallet pass not found"
        assert "request_id" in body["error"]
    finally:
        app.dependency_overrides.clear()


def test_wallet_passes_restore_conflict_returns_typed_error(monkeypatch) -> None:
    async def fake_restore(self: WalletPassService, wallet_pass_id, principal: AuthPrincipal):
        raise HTTPException(status_code=409, detail="Wallet pass is already active")

    monkeypatch.setattr(WalletPassService, "restore_wallet_pass", fake_restore)
    app.dependency_overrides[get_access_context] = lambda: _override_access_context("practitioner")
    app.dependency_overrides[get_db_session] = _override_db_session

    try:
        with TestClient(app) as client:
            response = client.post(f"/api/v1/wallet-passes/{uuid4()}/restore", json={"reason": "manual"})
        assert response.status_code == 409
        body = response.json()
        assert body["error"]["code"] == "http_error"
        assert body["error"]["message"] == "Wallet pass is already active"
        assert "request_id" in body["error"]
    finally:
        app.dependency_overrides.clear()
