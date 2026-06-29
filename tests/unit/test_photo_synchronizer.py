from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock

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


def _make_stub_candidate(path: Path) -> FileCandidate:
    """Return a FileCandidate for a path that may not exist on disk."""
    return FileCandidate(
        library_id="family",
        path=path,
        filename=path.name,
        size=0,
        modified_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_sync_skips_file_that_disappears_during_extraction(tmp_path: Path) -> None:
    good_path = tmp_path / "good.jpg"
    Image.new("RGB", (100, 50)).save(good_path)
    missing_path = tmp_path / "gone.jpg"
    Image.new("RGB", (100, 50)).save(missing_path)

    candidates = [_make_candidate(good_path), _make_candidate(missing_path)]
    missing_path.unlink()

    database = initialize_database(tmp_path / "frameflow.db")
    try:
        repository = PhotoRepository(database)
        synchronizer = PhotoSynchronizer(repository=repository, extractor=MetadataExtractor())

        processed = synchronizer.sync(candidates)

        assert processed == 1
        assert repository.count() == 1
    finally:
        database.close()


def test_sync_skips_file_on_permission_error(tmp_path: Path) -> None:
    good_path = tmp_path / "good.jpg"
    Image.new("RGB", (100, 50)).save(good_path)
    bad_path = tmp_path / "bad.jpg"

    def extract_or_raise(candidate: FileCandidate) -> object:
        if candidate.path == good_path:
            return MetadataExtractor().extract(candidate)
        raise PermissionError("access denied")

    extractor = Mock()
    extractor.extract.side_effect = extract_or_raise

    database = initialize_database(tmp_path / "frameflow.db")
    try:
        repository = PhotoRepository(database)
        synchronizer = PhotoSynchronizer(repository=repository, extractor=extractor)

        processed = synchronizer.sync(
            [_make_stub_candidate(good_path), _make_stub_candidate(bad_path)]
        )

        assert processed == 1
        assert repository.count() == 1
    finally:
        database.close()


def test_sync_skips_corrupt_image(tmp_path: Path) -> None:
    good_path = tmp_path / "good.jpg"
    Image.new("RGB", (100, 50)).save(good_path)
    corrupt_path = tmp_path / "corrupt.jpg"
    corrupt_path.write_bytes(b"this is not a valid image")

    database = initialize_database(tmp_path / "frameflow.db")
    try:
        repository = PhotoRepository(database)
        synchronizer = PhotoSynchronizer(repository=repository, extractor=MetadataExtractor())

        processed = synchronizer.sync(
            [_make_candidate(good_path), _make_stub_candidate(corrupt_path)]
        )

        assert processed == 1
        assert repository.count() == 1
    finally:
        database.close()


def test_sync_returns_zero_when_all_files_fail(tmp_path: Path) -> None:
    corrupt_path = tmp_path / "corrupt.jpg"
    corrupt_path.write_bytes(b"not an image")

    database = initialize_database(tmp_path / "frameflow.db")
    try:
        repository = PhotoRepository(database)
        synchronizer = PhotoSynchronizer(repository=repository, extractor=MetadataExtractor())

        processed = synchronizer.sync([_make_stub_candidate(corrupt_path)])

        assert processed == 0
        assert repository.count() == 0
    finally:
        database.close()


def test_sync_failed_file_is_not_marked_unavailable(tmp_path: Path) -> None:
    image_path = tmp_path / "photo.jpg"
    Image.new("RGB", (100, 50)).save(image_path)

    database = initialize_database(tmp_path / "frameflow.db")
    try:
        repository = PhotoRepository(database)
        synchronizer = PhotoSynchronizer(repository=repository, extractor=MetadataExtractor())

        synchronizer.sync([_make_candidate(image_path)])
        assert len(repository.list_all()) == 1

        extractor = Mock()
        extractor.extract.side_effect = PermissionError("access denied")
        failing_synchronizer = PhotoSynchronizer(repository=repository, extractor=extractor)
        failing_synchronizer.sync([_make_stub_candidate(image_path)])

        assert len(repository.list_all()) == 1
    finally:
        database.close()
