import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .api.v1.router import api_router
from .auth.dependencies import verifier
from .config import settings
from .db import engine
from .health.checks import check_db_schema, check_firebase_init, check_s3_access, check_stripe
from .observability import RequestContextMiddleware, configure_logging, register_exception_handlers
from .startup_validation import run_startup_validation, should_fail_startup

configure_logging(settings.log_level)
logger = logging.getLogger("app.main")

app = FastAPI(title="Superhero Platform API", version="0.1.0")
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)
app.include_router(api_router)


@app.on_event("startup")
async def startup_validation() -> None:
    try:
        await run_startup_validation()
        logger.info("startup.validation.ok", extra={"event": "startup.validation.ok"})
    except Exception as exc:
        logger.exception("startup.validation.failed", extra={"event": "startup.validation.failed"})
        if should_fail_startup(exc):
            raise


@app.get("/health")
async def health() -> dict[str, str]:
    logger.info("health.check", extra={"event": "health.check"})
    return {"status": "ok"}


@app.get("/health/db")
async def health_db() -> dict[str, str]:
    async with engine.connect() as conn:
        await conn.execute(text("select 1"))
    logger.info("health.db.check", extra={"event": "health.db.check"})
    return {"status": "ok"}


@app.get("/health/storage")
async def health_storage() -> dict[str, str]:
    check_s3_access()
    logger.info("health.storage.check", extra={"event": "health.storage.check"})
    return {"status": "ok"}


@app.get("/health/firebase")
async def health_firebase() -> dict[str, str]:
    result = check_firebase_init()
    if result["status"] != "ok":
        raise RuntimeError(result.get("detail", "Firebase health check failed"))
    logger.info("health.firebase.check", extra={"event": "health.firebase.check"})
    return {"status": "ok"}


@app.get("/health/stripe")
async def health_stripe() -> dict[str, str]:
    result = check_stripe()
    if result["status"] != "ok":
        raise RuntimeError(result.get("detail", "Stripe health check failed"))
    logger.info("health.stripe.check", extra={"event": "health.stripe.check"})
    return {"status": "ok"}


@app.get("/health/schema")
async def health_schema() -> dict[str, str]:
    result = await check_db_schema(engine, settings.db_schema)
    if result["status"] != "ok":
        raise RuntimeError(f'Database schema "{settings.db_schema}" does not exist')
    logger.info("health.schema.check", extra={"event": "health.schema.check"})
    return {"status": "ok"}


@app.get("/debug/firebase-auth")
async def debug_firebase_auth() -> dict[str, object | str | bool | None]:
    state = verifier.debug_state()
    logger.info("debug.firebase_auth", extra={"event": "debug.firebase_auth", **state})
    return state
