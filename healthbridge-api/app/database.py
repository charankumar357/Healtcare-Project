"""
Async SQLAlchemy engine and session factory.
All database operations use AsyncSession.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# ─── Async Engine ───
engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# ─── Session Factory ───
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ─── Base Model ───
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# ─── Dependency: get async DB session ───
async def get_db() -> AsyncSession:
    """FastAPI dependency — yields an async database session.

    Usage in routers:
        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ─── Health check helper ───
async def check_db_connection() -> bool:
    """Test database connectivity for /health endpoint."""
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        return True
    except Exception:
        return False
