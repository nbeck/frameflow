"""Configuration loading utilities."""

from .models import Settings


def load_settings() -> Settings:
    """Load and validate FrameFlow configuration."""

    return Settings()
