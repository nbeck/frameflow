"""Package marker. SPDX-License-Identifier: Apache-2.0"""

from fastapi import FastAPI

from frameflow.api.health import router as health_router
from frameflow.api.routes import photos_router, system_router


def create_app() -> FastAPI:
    """Create and configure the FrameFlow API application."""

    app = FastAPI(title="FrameFlow")

    app.include_router(health_router)
    app.include_router(photos_router)
    app.include_router(system_router)

    return app


app = create_app()
