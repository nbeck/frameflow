"""Photo service tests."""

from datetime import UTC, datetime
from pathlib import Path

from frameflow.domain import Photo
from frameflow.history import RotationHistoryRepository
from frameflow.rotation import RotationEngine
from frameflow.services import PhotoService
from frameflow.services.photo_selection import PhotoSelectionService
from frameflow.storage import PhotoRepository, initialize_database


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

        photo = Photo(
            id="hash-1",
            library_id="default",
            source_path=tmp_path / "photo.jpg",
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
            photo_repository.upsert(
                Photo(
                    id=f"hash-{i}",
                    library_id="default",
                    source_path=tmp_path / f"photo-{i}.jpg",
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
