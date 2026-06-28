"""Typed configuration models for FrameFlow."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .defaults import (
    DEFAULT_DATA_DIR,
    DEFAULT_DATABASE_PATH,
    DEFAULT_ENVIRONMENT,
    DEFAULT_HOST,
    DEFAULT_LOG_LEVEL,
    DEFAULT_PHOTO_LIBRARY,
    DEFAULT_PORT,
)


class Settings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_prefix="FRAMEFLOW_",
        env_file=".env",
        extra="ignore",
    )

    environment: str = Field(default=DEFAULT_ENVIRONMENT)
    host: str = Field(default=DEFAULT_HOST)
    port: int = Field(default=DEFAULT_PORT)

    data_dir: str = Field(default=DEFAULT_DATA_DIR)
    database_path: str = Field(default=DEFAULT_DATABASE_PATH)
    photo_library: str = Field(default=DEFAULT_PHOTO_LIBRARY)

    log_level: str = Field(default=DEFAULT_LOG_LEVEL)
