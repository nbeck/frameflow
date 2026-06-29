from datetime import UTC, datetime
from pathlib import Path

from frameflow.domain import Photo
from frameflow.storage import PhotoRepository, initialize_database


def test_photo_repository_insert(tmp_path: Path) -> None:
    database = initialize_database(tmp_path / "frameflow.db")
    modified_at = datetime(2026, 1, 1, tzinfo=UTC)

    try:
        repository = PhotoRepository(database)

        repository.upsert(
            Photo(
                id="abc123",
                library_id="family",
                source_path=Path("/photos/family.jpg"),
                content_hash="abc123",
                file_size=12345,
                width=640,
                height=480,
                image_format="JPEG",
                modified_at=modified_at,
            )
        )

        assert repository.count() == 1
    finally:
        database.close()


def test_photo_repository_get_by_id_returns_photo(tmp_path: Path) -> None:
    database = initialize_database(tmp_path / "frameflow.db")
    modified_at = datetime(2026, 1, 1, tzinfo=UTC)

    try:
        repository = PhotoRepository(database)
        photo = Photo(
            id="abc123",
            library_id="family",
            source_path=Path("/photos/family.jpg"),
            content_hash="abc123",
            file_size=12345,
            width=640,
            height=480,
            image_format="JPEG",
            modified_at=modified_at,
        )
        repository.upsert(photo)

        # Photo.id == content_hash in the current filesystem implementation
        result = repository.get_by_id("abc123")

        assert result is not None
        assert result.id == "abc123"
        assert result.source_path == Path("/photos/family.jpg")
    finally:
        database.close()


def test_photo_repository_get_by_id_returns_none_for_unknown_id(tmp_path: Path) -> None:
    database = initialize_database(tmp_path / "frameflow.db")

    try:
        repository = PhotoRepository(database)

        assert repository.get_by_id("does-not-exist") is None
    finally:
        database.close()


def test_photo_repository_upsert(tmp_path: Path) -> None:
    database = initialize_database(tmp_path / "frameflow.db")
    modified_at = datetime(2026, 1, 1, tzinfo=UTC)

    try:
        repository = PhotoRepository(database)

        photo = Photo(
            id="abc123",
            library_id="family",
            source_path=Path("/photos/family.jpg"),
            content_hash="abc123",
            file_size=12345,
            width=640,
            height=480,
            image_format="JPEG",
            modified_at=modified_at,
        )

        repository.upsert(photo)
        repository.upsert(photo)

        assert repository.count() == 1
    finally:
        database.close()
