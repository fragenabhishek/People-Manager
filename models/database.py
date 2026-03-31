"""
SQLAlchemy database engine, session factory, and Base.
Importable by repositories, Alembic, and the app factory.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


_engine = None
SessionLocal = None


def init_db(database_url: str, echo: bool = False):
    """Create the engine and session factory. Call once at app startup."""
    global _engine, SessionLocal

    connect_args = {}
    extra_kwargs = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        if ":memory:" in database_url:
            extra_kwargs["poolclass"] = StaticPool

    _engine = create_engine(database_url, echo=echo, connect_args=connect_args, **extra_kwargs)
    SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


def get_engine():
    return _engine


def get_session_factory():
    return SessionLocal


def create_tables():
    """Create all tables (useful for tests / first-run without Alembic)."""
    if _engine:
        Base.metadata.create_all(_engine)


def drop_tables():
    """Drop all tables (tests only)."""
    if _engine:
        Base.metadata.drop_all(_engine)
