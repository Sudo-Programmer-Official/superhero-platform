from __future__ import annotations

import os

from fastapi import HTTPException

from app.config import settings
from app.db import engine
from app.health.checks import check_db, check_db_schema, check_firebase_init, check_s3_access, check_stripe


def _missing_required_env() -> list[str]:
    missing: list[str] = []
    for key in settings.required_env_keys:
        if not os.getenv(key):
            missing.append(key)
    return missing


async def run_startup_validation() -> None:
    missing = _missing_required_env()
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")

    await check_db(engine)
    schema_check = await check_db_schema(engine, settings.db_schema)
    if schema_check["status"] != "ok":
        raise RuntimeError(f'Database schema "{settings.db_schema}" does not exist')

    firebase_check = check_firebase_init()
    if firebase_check["status"] != "ok":
        raise RuntimeError(f'Firebase init failed: {firebase_check.get("detail", "unknown error")}')

    s3_check = check_s3_access()
    if s3_check["status"] != "ok":
        raise RuntimeError(f'S3 access failed: {s3_check.get("detail", "unknown error")}')

    stripe_check = check_stripe()
    if stripe_check["status"] != "ok":
        raise RuntimeError(f'Stripe check failed: {stripe_check.get("detail", "unknown error")}')


def should_fail_startup(exc: Exception) -> bool:
    if settings.env.lower() == "test":
        return False
    if isinstance(exc, HTTPException):
        return settings.startup_validation_strict
    return settings.startup_validation_strict

