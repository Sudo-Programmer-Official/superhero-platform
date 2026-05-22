from __future__ import annotations

from typing import Any

import boto3
import stripe
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.config import settings
from app.auth.firebase_admin_init import get_or_init_firebase_app
from app.storage.s3_service import S3StorageService


async def check_db(engine: AsyncEngine) -> dict[str, Any]:
    async with engine.connect() as conn:
        await conn.execute(text("select 1"))
    return {"status": "ok"}


async def check_db_schema(engine: AsyncEngine, schema: str) -> dict[str, Any]:
    query = text(
        "select exists (select 1 from information_schema.schemata where schema_name = :schema_name) as exists_schema"
    )
    async with engine.connect() as conn:
        result = await conn.execute(query, {"schema_name": schema})
        exists_schema = bool(result.scalar())
    return {"status": "ok" if exists_schema else "error", "schema": schema, "exists": exists_schema}


def check_firebase_init() -> dict[str, Any]:
    if not settings.firebase_project_id:
        return {"status": "error", "detail": "FIREBASE_PROJECT_ID missing"}
    if not settings.firebase_service_account_json.strip() and not settings.firebase_service_account_path.strip():
        return {
            "status": "error",
            "detail": "Firebase Admin credentials missing. Set FIREBASE_SERVICE_ACCOUNT_JSON or FIREBASE_SERVICE_ACCOUNT_PATH",
        }
    try:
        import firebase_admin
    except Exception as exc:
        return {"status": "error", "detail": f"firebase_admin unavailable: {exc}"}

    try:
        get_or_init_firebase_app("health-check")
    except Exception as exc:
        return {"status": "error", "detail": f"firebase init failed: {exc}"}
    return {"status": "ok"}


def check_s3_access() -> dict[str, Any]:
    storage = S3StorageService()
    client = boto3.client("s3", region_name=storage.region)
    client.head_bucket(Bucket=storage.bucket)
    return {"status": "ok", "bucket": storage.bucket, "region": storage.region}


def check_stripe() -> dict[str, Any]:
    if settings.payments_test_mode:
        return {"status": "ok", "mode": "payments_test_mode"}
    if not settings.stripe_secret_key:
        return {"status": "error", "detail": "STRIPE_SECRET_KEY missing"}
    stripe.api_key = settings.stripe_secret_key
    stripe.Balance.retrieve()
    return {"status": "ok"}
