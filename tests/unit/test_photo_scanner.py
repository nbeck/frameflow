from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from frameflow.metadata import MetadataExtractor
from frameflow.providers import FileCandidate
from frameflow.scanning import PhotoScanner
from frameflow.services import PhotoSynchronizer
from frameflow.storage import PhotoRepository, initialize_database


class FakeProvider:
    def __init__(self, candidate: FileCandidate) -> None:
        self._candidate = candidate

    def discover(self) -> Iterable[FileCandidate]:
        return [self._candidate]


def test_photo_scanner_runs_scan(tmp_path: Path) -> None:
    image_path = tmp_path / "photo.jpg"

    from PIL import Image

    Image.new("RGB", (100, 50)).save(image_path)

    stat = image_path.stat()

    candidate = FileCandidate(
        library_id="family",
        path=image_path,
        filename=image_path.name,
        size=stat.st_size,
        modified_at=datetime.fromtimestamp(stat.st_mtime, UTC),
    )

    database = initialize_database(tmp_path / "frameflow.db")

    try:
        repository = PhotoRepository(database)
        synchronizer = PhotoSynchronizer(
            repository=repository,
            extractor=MetadataExtractor(),
        )

        scanner = PhotoScanner(
            provider=FakeProvider(candidate),
            synchronizer=synchronizer,
        )

        assert scanner.scan() == 1
    finally:
        database.close()
