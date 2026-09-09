"""Async database connection and session management for SQLite and PostgreSQL."""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


_is_sqlite = "sqlite" in settings.database_url

# Build connect_args.
# asyncpg does NOT reliably parse ?ssl=require from the URL query string —
# it must be passed via connect_args. Strip it from the URL and inject here.
connect_args: dict = {}
_db_url = settings.database_url

if _is_sqlite:
    connect_args["check_same_thread"] = False
else:
    # Strip any ?ssl=... query param from URL; pass SSL mode via connect_args
    if "?ssl=" in _db_url:
        _db_url, ssl_val = _db_url.split("?ssl=", 1)
        connect_args["ssl"] = ssl_val.split("&")[0]
    elif "?sslmode=" in _db_url:
        _db_url, _ = _db_url.split("?sslmode=", 1)
        connect_args["ssl"] = "require"
    else:
        # Supabase always requires SSL — enforce even if not in URL
        connect_args["ssl"] = "require"

engine = create_async_engine(
    _db_url,
    echo=False,
    connect_args=connect_args,
    future=True,
    pool_pre_ping=True,   # Test connections before use (handles stale connections)
    pool_recycle=300,     # Recycle connections every 5 min (avoids Supabase idle timeout)
)

# Enforce foreign key constraints for SQLite
if _is_sqlite:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables.

    SQLite (local dev): auto-creates tables from SQLAlchemy models.
    PostgreSQL (production): tables already exist from supabase/schema.sql.
      Only verifies connectivity — skips create_all to avoid conflicts with RLS.
      Logs a warning instead of crashing if DB is momentarily unreachable at startup.
    """
    import app.models  # noqa: F401

    if _is_sqlite:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("[DB] SQLite tables created/verified.")
    else:
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("[DB] PostgreSQL connectivity verified.")
        except Exception as exc:
            # Don't crash on startup — individual requests will surface the error
            logger.warning(
                "[DB] Could not verify PostgreSQL connectivity at startup: %s. "
                "Check DATABASE_URL environment variable.",
                exc,
            )
