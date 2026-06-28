"""Photo scanning service."""

from collections.abc import Iterable

from frameflow.providers import FileCandidate, FileProvider
from frameflow.services import PhotoSynchronizer


class PhotoScanner:
    """Coordinate discovery and synchronization."""

    def __init__(
        self,
        provider: FileProvider,
        synchronizer: PhotoSynchronizer,
    ) -> None:
        self._provider = provider
        self._synchronizer = synchronizer

    def scan(self) -> int:
        """Run a single scan."""

        candidates: Iterable[FileCandidate] = self._provider.discover()

        return self._synchronizer.sync(candidates)
