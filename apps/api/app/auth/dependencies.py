from fastapi import Depends, Header, HTTPException, status

from app.config import settings

from .firebase import FirebaseTokenVerifier
from .types import AuthPrincipal

verifier = FirebaseTokenVerifier(project_id=settings.firebase_project_id)


def _extract_bearer(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization scheme")
    return authorization[len(prefix) :].strip()


async def get_current_principal(authorization: str | None = Header(default=None)) -> AuthPrincipal:
    token = _extract_bearer(authorization)
    return verifier.verify(token)


def require_roles(*allowed_roles: str):
    async def _guard(principal: AuthPrincipal = Depends(get_current_principal)) -> AuthPrincipal:
        if principal.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return principal

    return _guard
