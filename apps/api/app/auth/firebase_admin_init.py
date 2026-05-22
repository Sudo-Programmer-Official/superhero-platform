from __future__ import annotations

import json
import logging
from typing import Any

from app.config import settings

logger = logging.getLogger("app.auth")


def _normalized_service_account_json() -> str:
    raw = settings.firebase_service_account_json.strip()
    if not raw:
        return ""
    # Some env UIs wrap JSON in quotes; unwrap once.
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        raw = raw[1:-1]
    return raw.strip()


def get_or_init_firebase_app(name: str = "auth-verifier"):
    import firebase_admin
    from firebase_admin import credentials

    # Reuse named app if already initialized.
    try:
        return firebase_admin.get_app(name)
    except ValueError:
        pass

    if not settings.firebase_project_id:
        raise RuntimeError("FIREBASE_PROJECT_ID is not configured")

    options = {"projectId": settings.firebase_project_id}
    credential_source = "none"

    service_account_json = _normalized_service_account_json()
    if service_account_json:
        try:
            info = json.loads(service_account_json)
        except json.JSONDecodeError as exc:
            raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON is not valid JSON") from exc
        cred = credentials.Certificate(info)
        credential_source = "env_json"
        app = firebase_admin.initialize_app(credential=cred, options=options, name=name)
        logger.info(
            "firebase.admin.initialized",
            extra={"event": "firebase.admin.initialized", "credential_source": credential_source},
        )
        return app

    if settings.firebase_service_account_path.strip():
        cred = credentials.Certificate(settings.firebase_service_account_path)
        credential_source = "file_path"
        app = firebase_admin.initialize_app(credential=cred, options=options, name=name)
        logger.info(
            "firebase.admin.initialized",
            extra={"event": "firebase.admin.initialized", "credential_source": credential_source},
        )
        return app

    raise RuntimeError(
        "Firebase Admin credentials missing. Set FIREBASE_SERVICE_ACCOUNT_JSON or FIREBASE_SERVICE_ACCOUNT_PATH."
    )


def get_app_debug_state(name: str = "auth-verifier") -> dict[str, Any]:
    import firebase_admin

    initialized = False
    app_name = None
    app_project_id = None
    credential_project_id = None

    try:
        app = firebase_admin.get_app(name)
        initialized = True
        app_name = app.name
        app_project_id = (getattr(app, "options", {}) or {}).get("projectId")
        credential_project_id = getattr(getattr(app, "credential", None), "project_id", None)
    except ValueError:
        initialized = False

    return {
        "configured_project_id": settings.firebase_project_id,
        "firebase_initialized": initialized,
        "firebase_app_name": app_name,
        "firebase_app_project_id": app_project_id,
        "firebase_credential_project_id": credential_project_id,
        "credential_source": (
            "env_json"
            if bool(_normalized_service_account_json())
            else ("file_path" if bool(settings.firebase_service_account_path.strip()) else "none")
        ),
        "check_revoked": settings.firebase_check_revoked,
    }
