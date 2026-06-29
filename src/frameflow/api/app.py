"""Package marker. SPDX-License-Identifier: Apache-2.0"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from frameflow.api.health import router as health_router
from frameflow.api.routes import photos_router, system_router
from frameflow.config import load_settings, validate_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    validate_settings(load_settings())
    yield


def create_app() -> FastAPI:
    """Create and configure the FrameFlow API application."""

    app = FastAPI(title="FrameFlow", lifespan=lifespan)

    app.include_router(health_router)
    app.include_router(photos_router)
    app.include_router(system_router)

    return app


app = create_app()
