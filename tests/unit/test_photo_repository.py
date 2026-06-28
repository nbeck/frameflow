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
                id="1",
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


def test_photo_repository_upsert(tmp_path: Path) -> None:
    database = initialize_database(tmp_path / "frameflow.db")
    modified_at = datetime(2026, 1, 1, tzinfo=UTC)

    try:
        repository = PhotoRepository(database)

        photo = Photo(
            id="1",
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
