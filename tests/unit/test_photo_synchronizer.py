from datetime import UTC, datetime
from pathlib import Path

import pytest
from PIL import Image

from frameflow.metadata import MetadataExtractor
from frameflow.providers import FileCandidate
from frameflow.services import PhotoSynchronizer
from frameflow.storage import PhotoRepository, initialize_database

pytestmark = pytest.mark.unit


def _make_candidate(path: Path) -> FileCandidate:
    stat = path.stat()
    return FileCandidate(
        library_id="family",
        path=path,
        filename=path.name,
        size=stat.st_size,
        modified_at=datetime.fromtimestamp(stat.st_mtime, UTC),
    )


def test_photo_synchronizer_sync(tmp_path: Path) -> None:
    image_path = tmp_path / "photo.jpg"
    Image.new("RGB", (100, 50)).save(image_path)

    database = initialize_database(tmp_path / "frameflow.db")

    try:
        repository = PhotoRepository(database)
        synchronizer = PhotoSynchronizer(
            repository=repository,
            extractor=MetadataExtractor(),
        )

        processed = synchronizer.sync([_make_candidate(image_path)])

        assert processed == 1
        assert repository.count() == 1
    finally:
        database.close()


def test_sync_marks_missing_photos_unavailable(tmp_path: Path) -> None:
    image_path = tmp_path / "photo.jpg"
    Image.new("RGB", (100, 50)).save(image_path)

    database = initialize_database(tmp_path / "frameflow.db")

    try:
        repository = PhotoRepository(database)
        synchronizer = PhotoSynchronizer(
            repository=repository,
            extractor=MetadataExtractor(),
        )

        synchronizer.sync([_make_candidate(image_path)])
        assert len(repository.list_all()) == 1

        image_path.unlink()
        synchronizer.sync([])

        assert repository.count() == 1
        assert repository.list_all() == []
    finally:
        database.close()


def test_sync_restores_photo_when_file_reappears(tmp_path: Path) -> None:
    image_path = tmp_path / "photo.jpg"
    Image.new("RGB", (100, 50)).save(image_path)

    database = initialize_database(tmp_path / "frameflow.db")

    try:
        repository = PhotoRepository(database)
        synchronizer = PhotoSynchronizer(
            repository=repository,
            extractor=MetadataExtractor(),
        )

        synchronizer.sync([_make_candidate(image_path)])
        image_path.unlink()
        synchronizer.sync([])
        assert repository.list_all() == []

        Image.new("RGB", (100, 50)).save(image_path)
        synchronizer.sync([_make_candidate(image_path)])

        assert len(repository.list_all()) == 1
    finally:
        database.close()
