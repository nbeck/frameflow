"""Photo synchronization service."""

from collections.abc import Iterable
from pathlib import Path

from frameflow.infrastructure.logging import get_logger
from frameflow.metadata import MetadataExtractor
from frameflow.providers import FileCandidate
from frameflow.storage import PhotoRepository

_logger = get_logger("frameflow.scanning.synchronizer")


class PhotoSynchronizer:
    """Synchronize discovered files into the photo repository."""

    def __init__(
        self,
        repository: PhotoRepository,
        extractor: MetadataExtractor,
    ) -> None:
        self._repository = repository
        self._extractor = extractor

    def sync(self, candidates: Iterable[FileCandidate]) -> int:
        """Synchronize all discovered photo candidates.

        Returns the number of successfully processed photos. Files that cannot
        be read or identified are skipped and do not affect the remaining sync.
        """
        processed = 0
        current_paths: set[Path] = set()

        for candidate in candidates:
            current_paths.add(candidate.path)
            try:
                photo = self._extractor.extract(candidate)
                self._repository.upsert(photo)
                processed += 1
            except OSError:
                _logger.warning(
                    "Skipping file during sync: %s",
                    candidate.path,
                    exc_info=True,
                )

        missing_paths = set(self._repository.list_paths()) - current_paths
        self._repository.mark_unavailable(missing_paths)
        if missing_paths:
            _logger.warning("Marked %d photo(s) as unavailable", len(missing_paths))

        return processed
