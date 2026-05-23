from typing import Final

PLATFORM_ADMIN_ROLES: Final[set[str]] = {
    "super_admin",
    "admin",
    "operator",
    "finance_admin",
    "support_admin",
    "moderator",
}

PRACTITIONER_ACCESS_ROLES: Final[set[str]] = {
    "super_admin",
    "admin",
    "practitioner",
}

BOOTSTRAP_ROLES: Final[set[str]] = {
    "customer",
    "practitioner",
    "admin",
    "super_admin",
}


def normalize_effective_role(role: str, has_practitioner_profile: bool) -> str:
    if role == "customer" and has_practitioner_profile:
        return "practitioner"
    return role


def is_platform_admin(role: str) -> bool:
    return role in PLATFORM_ADMIN_ROLES
