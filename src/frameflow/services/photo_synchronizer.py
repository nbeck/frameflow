"""Photo synchronization service."""

from collections.abc import Iterable
from pathlib import Path

from frameflow.metadata import MetadataExtractor
from frameflow.providers import FileCandidate
from frameflow.storage import PhotoRepository


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

        Returns the number of processed photos.
        """
        processed = 0
        current_paths: set[Path] = set()

        for candidate in candidates:
            current_paths.add(candidate.path)
            photo = self._extractor.extract(candidate)
            self._repository.upsert(photo)
            processed += 1

        self._repository.delete_missing(current_paths)

        return processed
