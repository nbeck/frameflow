"""Configuration loading utilities."""

from pathlib import Path

from .exceptions import ConfigurationError
from .models import Settings


def load_settings() -> Settings:
    """Load FrameFlow configuration from environment and .env file."""

    return Settings()


def validate_settings(settings: Settings) -> None:
    """Raise ConfigurationError if settings reference invalid paths."""

    library = Path(settings.photo_library)
    if not library.exists():
        raise ConfigurationError(f"Photo library path does not exist: {library}")
    if not library.is_dir():
        raise ConfigurationError(f"Photo library path is not a directory: {library}")

    db_parent = Path(settings.database_path).parent
    if db_parent.exists() and not db_parent.is_dir():
        raise ConfigurationError(f"Database path parent exists but is not a directory: {db_parent}")
