from dataclasses import dataclass


@dataclass
class AuthPrincipal:
    uid: str
    email: str | None
    role: str
