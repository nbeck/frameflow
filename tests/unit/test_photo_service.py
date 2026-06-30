"""Photo service tests."""

import threading
from datetime import UTC, datetime
from pathlib import Path

import pytest

from frameflow.domain import Photo
from frameflow.history import RotationHistoryRepository
from frameflow.rotation import RotationEngine
from frameflow.services import PhotoService
from frameflow.services.photo_selection import PhotoSelectionService
from frameflow.storage import PhotoRepository, initialize_database

pytestmark = pytest.mark.unit


def test_photo_service_returns_and_records_next_photo(tmp_path: Path) -> None:
    database = initialize_database(tmp_path / "frameflow.db")
    try:
        photo_repository = PhotoRepository(database)
        history_repository = RotationHistoryRepository(database)
        service = PhotoService(
            photo_repository=photo_repository,
            history_repository=history_repository,
            selection_service=PhotoSelectionService(RotationEngine()),
        )

        photo_path = tmp_path / "photo.jpg"
        photo_path.write_bytes(b"fake")
        photo = Photo(
            id="hash-1",
            library_id="default",
            source_path=photo_path,
            content_hash="hash-1",
            file_size=123,
            width=100,
            height=100,
            image_format="JPEG",
            modified_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
        photo_repository.upsert(photo)

        selected = service.get_next_photo("kitchen-dakboard")

        assert selected == photo

        history = history_repository.recent_for_client("kitchen-dakboard")

        assert len(history) == 1
        assert history[0].photo_id == "hash-1"
        assert history[0].client_id == "kitchen-dakboard"
    finally:
        database.close()


def test_photo_service_maintains_independent_history_per_client(tmp_path: Path) -> None:
    database = initialize_database(tmp_path / "frameflow.db")
    try:
        photo_repository = PhotoRepository(database)
        history_repository = RotationHistoryRepository(database)
        service = PhotoService(
            photo_repository=photo_repository,
            history_repository=history_repository,
            selection_service=PhotoSelectionService(RotationEngine()),
        )

        for i in (1, 2):
            photo_path = tmp_path / f"photo-{i}.jpg"
            photo_path.write_bytes(b"fake")
            photo_repository.upsert(
                Photo(
                    id=f"hash-{i}",
                    library_id="default",
                    source_path=photo_path,
                    content_hash=f"hash-{i}",
                    file_size=123,
                    width=100,
                    height=100,
                    image_format="JPEG",
                    modified_at=datetime(2026, 1, i, tzinfo=UTC),
                )
            )

        service.get_next_photo("client-a")
        service.get_next_photo("client-b")

        history_a = history_repository.recent_for_client("client-a")
        history_b = history_repository.recent_for_client("client-b")

        assert len(history_a) == 1
        assert all(e.client_id == "client-a" for e in history_a)
        assert len(history_b) == 1
        assert all(e.client_id == "client-b" for e in history_b)
    finally:
        database.close()


def test_photo_service_returns_none_when_no_photos(tmp_path: Path) -> None:
    database = initialize_database(tmp_path / "frameflow.db")
    try:
        service = PhotoService(
            photo_repository=PhotoRepository(database),
            history_repository=RotationHistoryRepository(database),
            selection_service=PhotoSelectionService(RotationEngine()),
        )

        assert service.get_next_photo("kitchen-dakboard") is None
    finally:
        database.close()


def test_get_next_photo_returns_none_when_source_file_missing(tmp_path: Path) -> None:
    database = initialize_database(tmp_path / "frameflow.db")
    try:
        photo_repository = PhotoRepository(database)
        history_repository = RotationHistoryRepository(database)
        service = PhotoService(
            photo_repository=photo_repository,
            history_repository=history_repository,
            selection_service=PhotoSelectionService(RotationEngine()),
        )

        missing_path = tmp_path / "gone.jpg"
        photo = Photo(
            id="hash-gone",
            library_id="default",
            source_path=missing_path,
            content_hash="hash-gone",
            file_size=123,
            width=100,
            height=100,
            image_format="JPEG",
            modified_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
        photo_repository.upsert(photo)

        result = service.get_next_photo("kitchen-dakboard")

        assert result is None
        assert history_repository.recent_for_client("kitchen-dakboard") == []
        assert photo_repository.list_all() == []
    finally:
        database.close()


def test_get_next_photo_rotates_through_all_photos(tmp_path: Path) -> None:
    # Regression: repeated calls must advance through all photos in the library,
    # not return the same photo every time.
    database = initialize_database(tmp_path / "frameflow.db")
    try:
        photo_repository = PhotoRepository(database)
        history_repository = RotationHistoryRepository(database)
        service = PhotoService(
            photo_repository=photo_repository,
            history_repository=history_repository,
            selection_service=PhotoSelectionService(RotationEngine()),
        )

        for i in range(1, 4):
            photo_path = tmp_path / f"photo-{i}.jpg"
            photo_path.write_bytes(b"fake")
            photo_repository.upsert(
                Photo(
                    id=f"hash-{i}",
                    library_id="default",
                    source_path=photo_path,
                    content_hash=f"hash-{i}",
                    file_size=4,
                    width=100,
                    height=100,
                    image_format="JPEG",
                    modified_at=datetime(2026, 1, i, tzinfo=UTC),
                )
            )

        ids = [service.get_next_photo("kitchen").id for _ in range(3)]  # type: ignore[union-attr]

        assert len(set(ids)) == 3, f"Expected 3 distinct photos, got: {ids}"
    finally:
        database.close()


def test_get_next_photo_is_safe_under_concurrent_requests(tmp_path: Path) -> None:
    # Regression: concurrent requests must not all select the same photo (TOCTOU
    # race) and must not raise InterfaceError from simultaneous sqlite3 access.
    database = initialize_database(tmp_path / "frameflow.db")
    try:
        photo_repository = PhotoRepository(database)

        for i in range(1, 4):
            photo_path = tmp_path / f"photo-{i}.jpg"
            photo_path.write_bytes(b"fake")
            photo_repository.upsert(
                Photo(
                    id=f"hash-{i}",
                    library_id="default",
                    source_path=photo_path,
                    content_hash=f"hash-{i}",
                    file_size=4,
                    width=100,
                    height=100,
                    image_format="JPEG",
                    modified_at=datetime(2026, 1, i, tzinfo=UTC),
                )
            )

        results: list[str | None] = []
        errors: list[Exception] = []
        barrier = threading.Barrier(4)

        def call_service() -> None:
            service = PhotoService(
                photo_repository=PhotoRepository(database),
                history_repository=RotationHistoryRepository(database),
                selection_service=PhotoSelectionService(RotationEngine()),
            )
            try:
                barrier.wait()
                photo = service.get_next_photo("kitchen")
                results.append(photo.id if photo else None)
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=call_service) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Concurrent requests raised: {errors}"
        assert len(results) == 4
        # All 3 photos must appear; the 4th call wraps back to the first
        unique_photos = {r for r in results if r is not None}
        assert len(unique_photos) == 3, f"Rotation did not advance through all photos: {results}"
    finally:
        database.close()


def test_get_next_photo_does_not_record_history_for_missing_file(tmp_path: Path) -> None:
    # "hash-a" (present) sorts before "hash-z" (missing), so the present photo
    # is selected first and history is recorded. On the second call, "hash-z"
    # is LRU and selected — but the file is missing so None is returned and
    # no history entry is created for it.
    database = initialize_database(tmp_path / "frameflow.db")
    try:
        photo_repository = PhotoRepository(database)
        history_repository = RotationHistoryRepository(database)
        service = PhotoService(
            photo_repository=photo_repository,
            history_repository=history_repository,
            selection_service=PhotoSelectionService(RotationEngine()),
        )

        present_path = tmp_path / "present.jpg"
        present_path.write_bytes(b"fake")
        missing_path = tmp_path / "gone.jpg"

        photo_repository.upsert(
            Photo(
                id="hash-a",
                library_id="default",
                source_path=present_path,
                content_hash="hash-a",
                file_size=4,
                width=100,
                height=100,
                image_format="JPEG",
                modified_at=datetime(2026, 1, 1, tzinfo=UTC),
            )
        )
        photo_repository.upsert(
            Photo(
                id="hash-z",
                library_id="default",
                source_path=missing_path,
                content_hash="hash-z",
                file_size=4,
                width=100,
                height=100,
                image_format="JPEG",
                modified_at=datetime(2026, 1, 2, tzinfo=UTC),
            )
        )

        first = service.get_next_photo("kitchen-dakboard")
        assert first is not None and first.id == "hash-a"

        second = service.get_next_photo("kitchen-dakboard")
        assert second is None

        history = history_repository.recent_for_client("kitchen-dakboard")
        assert len(history) == 1
        assert history[0].photo_id == "hash-a"

        available = photo_repository.list_all()
        assert len(available) == 1
        assert available[0].id == "hash-a"
    finally:
        database.close()
