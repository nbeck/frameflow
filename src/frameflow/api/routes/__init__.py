"""API routes."""

from .display import router as display_router
from .photos import router as photos_router
from .system import router as system_router

__all__ = ["display_router", "photos_router", "system_router"]
