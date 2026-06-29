"""API dependency providers."""

import sqlite3
from functools import lru_cache
from pathlib import Path

from frameflow.config import Settings, load_settings
from frameflow.history import RotationHistoryRepository
from frameflow.rotation import RotationEngine
from frameflow.services import PhotoService
from frameflow.services.photo_selection import PhotoSelectionService
from frameflow.storage import PhotoRepository


@lru_cache
def get_settings() -> Settings:
    """Return the application settings."""

    return load_settings()


@lru_cache
def get_database_connection() -> sqlite3.Connection:
    """Return the shared SQLite database connection."""

    settings = load_settings()
    database_path = Path(settings.database_path)
    return sqlite3.connect(database_path)


def get_photo_service() -> PhotoService:
    """Return the photo service."""

    connection = get_database_connection()
    return PhotoService(
        photo_repository=PhotoRepository(connection),
        history_repository=RotationHistoryRepository(connection),
        selection_service=PhotoSelectionService(RotationEngine()),
    )
