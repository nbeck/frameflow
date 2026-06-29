from datetime import UTC, datetime
from pathlib import Path

import pytest

from frameflow.domain import Photo
from frameflow.storage import PhotoRepository, initialize_database

pytestmark = pytest.mark.unit


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


def _make_photo(n: int) -> Photo:
    return Photo(
        id=f"hash-{n}",
        library_id="family",
        source_path=Path(f"/photos/photo-{n}.jpg"),
        content_hash=f"hash-{n}",
        file_size=100,
        width=100,
        height=100,
        image_format="JPEG",
        modified_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_list_all_excludes_unavailable_photos(tmp_path: Path) -> None:
    database = initialize_database(tmp_path / "frameflow.db")

    try:
        repository = PhotoRepository(database)
        repository.upsert(_make_photo(1))
        repository.upsert(_make_photo(2))

        repository.mark_unavailable({Path("/photos/photo-1.jpg")})

        photos = repository.list_all()

        assert len(photos) == 1
        assert photos[0].id == "hash-2"
    finally:
        database.close()


def test_upsert_restores_available_flag(tmp_path: Path) -> None:
    database = initialize_database(tmp_path / "frameflow.db")

    try:
        repository = PhotoRepository(database)
        photo = _make_photo(1)
        repository.upsert(photo)
        repository.mark_unavailable({photo.source_path})

        assert repository.list_all() == []

        repository.upsert(photo)

        assert len(repository.list_all()) == 1
    finally:
        database.close()


def test_mark_unavailable_returns_actual_rows_updated(tmp_path: Path) -> None:
    database = initialize_database(tmp_path / "frameflow.db")

    try:
        repository = PhotoRepository(database)
        repository.upsert(_make_photo(1))
        repository.upsert(_make_photo(2))

        count = repository.mark_unavailable(
            {
                Path("/photos/photo-1.jpg"),
                Path("/photos/photo-2.jpg"),
                Path("/photos/does-not-exist.jpg"),
            }
        )

        assert count == 2
    finally:
        database.close()


def test_mark_unavailable_empty_set_returns_zero(tmp_path: Path) -> None:
    database = initialize_database(tmp_path / "frameflow.db")

    try:
        repository = PhotoRepository(database)

        assert repository.mark_unavailable(set()) == 0
    finally:
        database.close()
