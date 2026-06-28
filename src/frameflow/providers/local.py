"""Local filesystem file provider."""

from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

from .models import FileCandidate

SUPPORTED_IMAGE_EXTENSIONS = frozenset(
    {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".heic",
        ".heif",
    }
)


class LocalFileProvider:
    """Discovers image files from a local filesystem photo library."""

    def __init__(self, library_id: str, root_path: Path) -> None:
        self.library_id = library_id
        self.root_path = root_path

    def discover(self) -> Iterable[FileCandidate]:
        """Return image candidates discovered under the root path."""
        if not self.root_path.exists() or not self.root_path.is_dir():
            return []

        candidates: list[FileCandidate] = []

        for path in self.root_path.rglob("*"):
            if self._should_skip(path):
                continue

            stat = path.stat()

            candidates.append(
                FileCandidate(
                    library_id=self.library_id,
                    path=path,
                    filename=path.name,
                    size=stat.st_size,
                    modified_at=datetime.fromtimestamp(stat.st_mtime),
                )
            )

        return candidates

    def _should_skip(self, path: Path) -> bool:
        """Return True if the path should not be considered."""

        if any(part.startswith(".") for part in path.parts):
            return True

        if not path.is_file():
            return True

        return path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS
