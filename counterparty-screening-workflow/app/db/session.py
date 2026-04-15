from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


def build_connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def ensure_database_path(database_url: str) -> None:
    if not database_url.startswith("sqlite"):
        return

    database_target = database_url.removeprefix("sqlite:///")
    if database_target == ":memory:" or database_target.startswith("file:"):
        return

    database_path = Path(database_target).expanduser()
    database_path.parent.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    settings = get_settings()
    ensure_database_path(settings.database_url)
    return create_engine(
        settings.database_url,
        future=True,
        pool_pre_ping=True,
        connect_args=build_connect_args(settings.database_url),
    )


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(
        bind=get_engine(),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )



def dispose_engine() -> None:
    get_engine().dispose()
    get_engine.cache_clear()
    get_session_factory.cache_clear()


def get_db() -> Generator[Session, None, None]:
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()
