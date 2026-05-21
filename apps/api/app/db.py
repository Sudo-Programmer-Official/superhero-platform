from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from .config import settings

engine: AsyncEngine = create_async_engine(
    settings.database_url_async,
    future=True,
    connect_args={"server_settings": {"search_path": settings.db_schema}},
)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
