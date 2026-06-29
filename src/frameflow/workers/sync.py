"""Background synchronization entry point."""

import sqlite3
import threading
from pathlib import Path

from frameflow.config import Settings
from frameflow.infrastructure.logging import get_logger
from frameflow.metadata import MetadataExtractor
from frameflow.providers.local import LocalFileProvider
from frameflow.scanning import PhotoScanner, ScanScheduler, SyncAlreadyRunningError, SyncState
from frameflow.services import PhotoSynchronizer
from frameflow.storage import PhotoRepository

_logger = get_logger("frameflow.workers.sync")

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


class SyncLoop:
    """Background thread that runs ScanScheduler.run_once() on a fixed interval.

    Waits one full interval before the first run, then repeats. The stop_event
    is set by stop() to unblock the wait and exit cleanly mid-interval.
    """

    def __init__(self, scheduler: ScanScheduler, interval_seconds: float) -> None:
        self._scheduler = scheduler
        self._interval = interval_seconds
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the background sync loop in a daemon thread.

        Safe to call multiple times — a second call while the thread is alive is a no-op.
        """
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="frameflow-sync-loop",
        )
        self._thread.start()
        _logger.info("Scheduled sync loop started (interval=%.0fs)", self._interval)

    def stop(self) -> None:
        """Signal the loop to stop and block until the thread exits."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None
        _logger.info("Scheduled sync loop stopped")

    def _run(self) -> None:
        while not self._stop_event.wait(timeout=self._interval):
            try:
                count = self._scheduler.run_once()
                _logger.info("Scheduled sync completed: %d photos processed", count)
            except SyncAlreadyRunningError:
                _logger.debug("Scheduled sync skipped: sync already in progress")
            except Exception:
                _logger.error("Scheduled sync failed", exc_info=True)


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
