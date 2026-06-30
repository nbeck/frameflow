"""API response models for FrameFlow."""

from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response model for GET /health."""

    status: str


class PhotoSummary(BaseModel):
    """A single photo entry returned by GET /photos."""

    id: str
    source_path: str


class StatusResponse(BaseModel):
    """Response model for GET /status."""

    status: str
    library_path: str
    library_exists: bool
    photo_count: int
    last_sync_completed_at: str | None
    last_sync_photos_processed: int | None
    sync_running: bool


class SyncResponse(BaseModel):
    """Response model for POST /sync."""

    status: str
    photos_processed: int
    sync_completed_at: str


class ConfigResponse(BaseModel):
    """Response model for GET /config."""

    library_path: str
    environment: str
    log_level: str
    supported_extensions: list[str]
