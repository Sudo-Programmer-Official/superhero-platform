from __future__ import annotations

import logging
from typing import Any

from fastapi import HTTPException, status

from .types import AuthPrincipal

logger = logging.getLogger("app.auth")


class FirebaseTokenVerifier:
    def __init__(self, project_id: str):
        self.project_id = project_id

    def verify(self, token: str) -> AuthPrincipal:
        # Production path: firebase-admin verify_id_token.
        try:
            import firebase_admin
            from firebase_admin import auth
        except Exception as exc:  # pragma: no cover
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase auth verifier unavailable",
            ) from exc

        if not firebase_admin._apps:  # type: ignore[attr-defined]
            firebase_admin.initialize_app()

        try:
            claims: dict[str, Any] = auth.verify_id_token(token, check_revoked=True)
        except Exception as exc:
            logger.warning("firebase.verify.failed", extra={"event": "firebase.verify.failed"})
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth token") from exc

        role = claims.get("role") or "customer"
        return AuthPrincipal(uid=claims["uid"], email=claims.get("email"), role=role)
