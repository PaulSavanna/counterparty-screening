from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

from app.core.config import Settings
from app.db.session import ensure_database_path


def run_migrations(settings: Settings) -> None:
    ensure_database_path(settings.database_url)

    project_root = Path(__file__).resolve().parents[2]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "migrations"))
    config.set_main_option("sqlalchemy.url", settings.database_url)

    command.upgrade(config, "head")
