import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .api.v1.router import api_router
from .config import settings
from .db import engine
from .observability import RequestContextMiddleware, configure_logging, register_exception_handlers

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
