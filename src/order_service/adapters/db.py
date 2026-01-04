from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from order_service.config import Settings, get_settings


def _create_engine(settings: Settings) -> Engine:
    connect_args: dict[str, object] = {}
    if settings.database_url.startswith("sqlite:"):
        connect_args["check_same_thread"] = False

    return create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)


_settings = get_settings()
engine: Engine = _create_engine(_settings)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    from order_service.adapters.models import Base

    Base.metadata.create_all(bind=engine)
