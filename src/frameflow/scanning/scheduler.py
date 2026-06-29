"""Background scan scheduler."""

from dataclasses import dataclass
from datetime import UTC, datetime

from frameflow.scanning.scanner import PhotoScanner


@dataclass
class SyncState:
    """In-memory record of the most recent sync run."""

    last_sync_completed_at: datetime | None = None
    last_sync_photos_processed: int | None = None
    sync_running: bool = False


class ScanScheduler:
    """Trigger background scans."""

    def __init__(self, scanner: PhotoScanner, sync_state: SyncState | None = None) -> None:
        self._scanner = scanner
        self._state = sync_state or SyncState()

    def run_once(self) -> int:
        """Run a single scan immediately."""

        self._state.sync_running = True
        try:
            count = self._scanner.scan()
        finally:
            self._state.sync_running = False

        self._state.last_sync_completed_at = datetime.now(UTC)
        self._state.last_sync_photos_processed = count
        return count
