from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.migrations import run_migrations
from app.db.session import dispose_engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    configure_logging()

    if settings.auto_migrate_on_startup:
        run_migrations(settings)

    yield

    dispose_engine()



def create_app() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix=settings.api_prefix)
    return application


app = create_app()
