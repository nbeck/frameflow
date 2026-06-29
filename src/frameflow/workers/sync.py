"""Background synchronization entry point."""

import sqlite3
from pathlib import Path

from frameflow.config import Settings
from frameflow.metadata import MetadataExtractor
from frameflow.providers.local import LocalFileProvider
from frameflow.scanning import PhotoScanner, ScanScheduler, SyncState
from frameflow.services import PhotoSynchronizer
from frameflow.storage import PhotoRepository

_LIBRARY_ID = "default"

_sync_state = SyncState()
_shared_scheduler: ScanScheduler | None = None


def get_sync_state() -> SyncState:
    """Return the shared in-memory sync state."""

    return _sync_state


def get_shared_scheduler(
    settings: Settings,
    connection: sqlite3.Connection,
) -> ScanScheduler:
    """Return the shared ScanScheduler singleton, creating it on first call."""

    global _shared_scheduler
    if _shared_scheduler is None:
        _shared_scheduler = build_scan_scheduler(settings, connection)
    return _shared_scheduler


def build_scan_scheduler(
    settings: Settings,
    connection: sqlite3.Connection,
) -> ScanScheduler:
    """Build a fully wired ScanScheduler from application settings."""

    provider = LocalFileProvider(
        library_id=_LIBRARY_ID,
        root_path=Path(settings.photo_library),
    )
    synchronizer = PhotoSynchronizer(
        repository=PhotoRepository(connection),
        extractor=MetadataExtractor(),
    )
    scanner = PhotoScanner(provider=provider, synchronizer=synchronizer)
    return ScanScheduler(scanner=scanner, sync_state=_sync_state)
