"""API routes."""

from .photos import router as photos_router
from .system import router as system_router

__all__ = ["photos_router", "system_router"]
