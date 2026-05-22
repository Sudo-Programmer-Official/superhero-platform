import logging

from fastapi import Depends, Header, HTTPException, status

from app.config import settings

from .firebase import FirebaseTokenVerifier
from .types import AuthPrincipal

verifier = FirebaseTokenVerifier(project_id=settings.firebase_project_id)
logger = logging.getLogger("app.auth")


def _extract_bearer(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization scheme")
    return authorization[len(prefix) :].strip()


async def get_current_principal(authorization: str | None = Header(default=None)) -> AuthPrincipal:
    logger.info(
        "auth.header.received",
        extra={
            "event": "auth.header.received",
            "has_authorization_header": bool(authorization),
            "authorization_prefix": authorization[:12] if authorization else None,
        },
    )
    token = _extract_bearer(authorization)
    logger.info(
        "auth.token.extracted",
        extra={
            "event": "auth.token.extracted",
            "token_prefix": token[:25],
            "token_length": len(token),
        },
    )
    return verifier.verify(token)


def require_roles(*allowed_roles: str):
    async def _guard(principal: AuthPrincipal = Depends(get_current_principal)) -> AuthPrincipal:
        if principal.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return principal

    return _guard
