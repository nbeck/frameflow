from datetime import UTC, datetime
from pathlib import Path

from PIL import Image

from frameflow.metadata import MetadataExtractor
from frameflow.providers import FileCandidate
from frameflow.services import PhotoSynchronizer
from frameflow.storage import PhotoRepository, initialize_database


def test_photo_synchronizer_sync(tmp_path: Path) -> None:
    image_path = tmp_path / "photo.jpg"
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

        processed = synchronizer.sync([candidate])

        assert processed == 1
        assert repository.count() == 1
    finally:
        database.close()


def test_photo_synchronizer_removes_deleted_photos(tmp_path: Path) -> None:
    image_path = tmp_path / "photo.jpg"
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

        synchronizer.sync([candidate])
        assert repository.count() == 1

        image_path.unlink()

        synchronizer.sync([])

        assert repository.count() == 0
    finally:
        database.close()
