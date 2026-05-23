from dataclasses import dataclass
from uuid import UUID


@dataclass
class AuthPrincipal:
    uid: str
    email: str | None
    role: str


@dataclass
class AccessContext:
    principal: AuthPrincipal
    tenant_id: str
    practitioner_id: UUID | None
    role: str
