from __future__ import annotations

import logging
import json
from base64 import urlsafe_b64decode
from typing import Any

from fastapi import HTTPException, status

from app.config import settings
from .firebase_admin_init import get_app_debug_state, get_or_init_firebase_app

from .types import AuthPrincipal

logger = logging.getLogger("app.auth")


class FirebaseTokenVerifier:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self._app = None
        self._app_name = "auth-verifier"

    @staticmethod
    def _decode_unverified_payload(token: str) -> dict[str, Any]:
        try:
            payload = token.split(".")[1]
            padded = payload + "=" * ((4 - len(payload) % 4) % 4)
            raw = urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8")
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
        return {}

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

        if self._app is None:
            if not self.project_id:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="FIREBASE_PROJECT_ID is not configured",
                )
            self._app = get_or_init_firebase_app(self._app_name)

        try:
            claims: dict[str, Any] = auth.verify_id_token(
                token,
                check_revoked=settings.firebase_check_revoked,
                app=self._app,
            )
        except Exception as exc:
            payload = self._decode_unverified_payload(token)
            logger.warning(
                "firebase.verify.failed",
                extra={
                    "event": "firebase.verify.failed",
                    "error": exc.__class__.__name__,
                    "detail": str(exc),
                    "project_id": self.project_id,
                    "token_aud": payload.get("aud"),
                    "token_iss": payload.get("iss"),
                    "token_sub": payload.get("sub"),
                },
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth token") from exc

        role = claims.get("role") or "customer"
        return AuthPrincipal(uid=claims["uid"], email=claims.get("email"), role=role)

    def debug_state(self) -> dict[str, Any]:
        return get_app_debug_state(self._app_name)
