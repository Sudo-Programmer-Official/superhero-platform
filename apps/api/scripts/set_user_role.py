from __future__ import annotations

import os
import sys
from argparse import ArgumentParser

# Allow running as: python3 scripts/set_user_role.py from apps/api
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.auth.firebase_admin_init import get_or_init_firebase_app
from app.config import settings
from app.domain.permissions import BOOTSTRAP_ROLES, PLATFORM_ADMIN_ROLES

ALLOWED_ROLES = sorted(BOOTSTRAP_ROLES | PLATFORM_ADMIN_ROLES)


def parse_args() -> tuple[str | None, str | None, str, bool]:
    parser = ArgumentParser(description="Set Firebase custom-claim role for a user (dev/staging helper).")
    parser.add_argument("--uid", help="Firebase Auth UID")
    parser.add_argument("--email", help="Firebase Auth email")
    parser.add_argument("--role", default="super_admin", choices=ALLOWED_ROLES, help="Role claim to set")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow execution outside development/test environments",
    )
    args = parser.parse_args()

    if not args.uid and not args.email:
        parser.error("Provide either --uid or --email")

    return args.uid, args.email, args.role, args.force


def assert_safe_environment(force: bool) -> None:
    env = (settings.env or "").lower().strip()
    allowed = {"development", "dev", "local", "test", "staging"}
    if env not in allowed and not force:
        raise RuntimeError(
            f"Refusing to modify claims in env='{settings.env}'. Re-run with --force if this is intentional."
        )


def main() -> None:
    uid, email, role, force = parse_args()
    assert_safe_environment(force)

    app = get_or_init_firebase_app(name="role-bootstrap")

    from firebase_admin import auth

    user = auth.get_user(uid=uid, app=app) if uid else auth.get_user_by_email(email=email or "", app=app)
    existing_claims = dict(user.custom_claims or {})
    existing_claims["role"] = role
    auth.set_custom_user_claims(user.uid, existing_claims, app=app)

    refreshed = auth.get_user(user.uid, app=app)
    final_claims = dict(refreshed.custom_claims or {})

    print("Updated Firebase custom claims")
    print(f"uid: {refreshed.uid}")
    print(f"email: {refreshed.email}")
    print(f"role: {final_claims.get('role')}")
    print(f"claims: {final_claims}")
    print("Done. Sign out and sign back in so /me reflects the new role.")


if __name__ == "__main__":
    main()
