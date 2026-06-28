from fastapi import FastAPI

from frameflow.api.health import router as health_router


def create_app() -> FastAPI:
    """Create and configure the FrameFlow API application."""

    app = FastAPI(title="FrameFlow")

    app.include_router(health_router)

    return app


app = create_app()
