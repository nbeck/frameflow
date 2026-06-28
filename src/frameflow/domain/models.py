"""Core domain models for FrameFlow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Library:
    """A photo library managed by FrameFlow."""

    id: str
    name: str
    root_path: Path


@dataclass(frozen=True)
class Album:
    """A collection of photos within a library."""

    id: str
    library_id: str
    name: str


@dataclass(frozen=True)
class Photo:
    """A photo known to FrameFlow."""

    id: str
    library_id: str
    source_path: Path

    content_hash: str | None = None
    file_size: int = 0
    width: int = 0
    height: int = 0
    image_format: str = ""
    modified_at: datetime | None = None


@dataclass(frozen=True)
class Client:
    """A display client that consumes FrameFlow photos."""

    id: str
    name: str
    client_type: str


@dataclass(frozen=True)
class DisplayEvent:
    """A record of a photo being displayed by a client."""

    photo_id: str
    client_id: str
    displayed_at: datetime
