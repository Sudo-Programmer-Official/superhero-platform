import logging

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db_session
from app.repositories.practitioner_repository import PractitionerRepository

from .firebase import FirebaseTokenVerifier
from .types import AccessContext, AuthPrincipal

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


async def require_authenticated_user(principal: AuthPrincipal = Depends(get_current_principal)) -> AuthPrincipal:
    return principal


async def get_access_context(
    principal: AuthPrincipal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
    x_tenant_id: str | None = Header(default=None),
) -> AccessContext:
    tenant_id = (x_tenant_id or settings.db_schema).strip()
    if tenant_id != settings.db_schema:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cross-tenant access denied")

    practitioner = await PractitionerRepository(session).get_by_firebase_uid(principal.uid)
    role = principal.role
    if role == "customer" and practitioner:
        role = "practitioner"

    return AccessContext(
        principal=AuthPrincipal(uid=principal.uid, email=principal.email, role=role),
        tenant_id=tenant_id,
        practitioner_id=practitioner.id if practitioner else None,
        role=role,
    )


def require_practitioner():
    async def _guard(ctx: AccessContext = Depends(get_access_context)) -> AuthPrincipal:
        if ctx.role not in {"super_admin", "admin", "practitioner"}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Practitioner access required")
        if ctx.role == "practitioner" and not ctx.practitioner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Practitioner profile not linked")
        return ctx.principal

    return _guard


def require_tenant_access(*allowed_roles: str):
    async def _guard(ctx: AccessContext = Depends(get_access_context)) -> AccessContext:
        if allowed_roles and ctx.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        if ctx.role == "practitioner" and not ctx.practitioner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Practitioner profile not linked")
        return ctx

    return _guard


def require_roles(*allowed_roles: str):
    async def _guard(principal: AuthPrincipal = Depends(get_current_principal)) -> AuthPrincipal:
        if principal.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return principal

    return _guard
