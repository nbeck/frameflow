"""Image metadata extraction."""

from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image

from frameflow.domain import Photo
from frameflow.providers import FileCandidate


class MetadataExtractor:
    """Extract metadata from image files."""

    def extract(self, candidate: FileCandidate) -> Photo:
        """Build a Photo from a discovered file."""

        with Image.open(candidate.path) as image:
            width, height = image.size
            image_format = image.format or ""

        content_hash = self._sha256(candidate.path)

        return Photo(
            id=content_hash,
            library_id=candidate.library_id,
            source_path=candidate.path,
            content_hash=content_hash,
            file_size=candidate.size,
            width=width,
            height=height,
            image_format=image_format,
            modified_at=candidate.modified_at,
        )

    @staticmethod
    def _sha256(path: Path) -> str:
        """Return the SHA-256 hash of a file."""

        digest = hashlib.sha256()

        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(8192), b""):
                digest.update(chunk)

        return digest.hexdigest()
