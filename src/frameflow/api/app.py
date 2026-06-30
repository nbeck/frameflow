"""Package marker. SPDX-License-Identifier: Apache-2.0"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from frameflow.api.dependencies import get_database_connection
from frameflow.api.health import router as health_router
from frameflow.api.routes import photos_router, system_router
from frameflow.config import load_settings, validate_settings
from frameflow.infrastructure.logging import configure_logging, get_logger
from frameflow.workers import SyncLoop
from frameflow.workers.sync import get_shared_scheduler

_logger = get_logger("frameflow.api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging()
    settings = load_settings()
    validate_settings(settings)
    _logger.info(
        "FrameFlow starting (environment=%s, library=%s, database=%s, sync_enabled=%s)",
        settings.environment,
        settings.photo_library,
        settings.database_path,
        settings.sync_enabled,
    )
    sync_loop: SyncLoop | None = None
    if settings.sync_enabled:
        scheduler = get_shared_scheduler(settings, get_database_connection())
        sync_loop = SyncLoop(scheduler=scheduler, interval_seconds=settings.sync_interval_seconds)
        sync_loop.start()
    try:
        yield
    finally:
        _logger.info("FrameFlow shutting down")
        if sync_loop is not None:
            sync_loop.stop()


def create_app() -> FastAPI:
    """Create and configure the FrameFlow API application."""

    app = FastAPI(title="FrameFlow", lifespan=lifespan)

    app.include_router(health_router)
    app.include_router(photos_router)
    app.include_router(system_router)

    return app


app = create_app()
