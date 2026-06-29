import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from frameflow.domain import DisplayEvent, Photo
from frameflow.history import RotationHistoryRepository
from frameflow.storage import PhotoRepository, initialize_database


def _create_photo(
    database: sqlite3.Connection,
    photo_number: int,
    source_path: str,
) -> None:
    repository = PhotoRepository(database)
    repository.upsert(
        Photo(
            id=f"hash-{photo_number}",
            library_id="default",
            source_path=Path(source_path),
            content_hash=f"hash-{photo_number}",
            file_size=100,
            width=1920,
            height=1080,
            image_format="JPEG",
            modified_at=datetime(2026, 1, photo_number, tzinfo=UTC),
        )
    )


def test_rotation_history_repository_records_event(tmp_path: Path) -> None:
    database = initialize_database(tmp_path / "frameflow.db")

    try:
        _create_photo(database, 1, "/photos/photo-1.jpg")
        repository = RotationHistoryRepository(database)

        repository.record(
            DisplayEvent(
                photo_id="hash-1",
                client_id="kitchen-dakboard",
                displayed_at=datetime(2026, 1, 1, tzinfo=UTC),
            )
        )

        assert repository.count() == 1
    finally:
        database.close()


def test_rotation_history_repository_returns_recent_events_for_client(
    tmp_path: Path,
) -> None:
    database = initialize_database(tmp_path / "frameflow.db")

    try:
        _create_photo(database, 1, "/photos/photo-1.jpg")
        _create_photo(database, 2, "/photos/photo-2.jpg")
        _create_photo(database, 3, "/photos/photo-3.jpg")
        repository = RotationHistoryRepository(database)

        older_event = DisplayEvent(
            photo_id="hash-1",
            client_id="kitchen-dakboard",
            displayed_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
        newer_event = DisplayEvent(
            photo_id="hash-2",
            client_id="kitchen-dakboard",
            displayed_at=datetime(2026, 1, 2, tzinfo=UTC),
        )
        other_client_event = DisplayEvent(
            photo_id="hash-3",
            client_id="office-dakboard",
            displayed_at=datetime(2026, 1, 3, tzinfo=UTC),
        )

        repository.record(older_event)
        repository.record(newer_event)
        repository.record(other_client_event)

        events = repository.recent_for_client("kitchen-dakboard")

        assert events == [newer_event, older_event]
    finally:
        database.close()


def test_rotation_history_repository_respects_limit(tmp_path: Path) -> None:
    database = initialize_database(tmp_path / "frameflow.db")

    try:
        _create_photo(database, 1, "/photos/photo-1.jpg")
        _create_photo(database, 2, "/photos/photo-2.jpg")
        repository = RotationHistoryRepository(database)

        repository.record(
            DisplayEvent(
                photo_id="hash-1",
                client_id="kitchen-dakboard",
                displayed_at=datetime(2026, 1, 1, tzinfo=UTC),
            )
        )
        repository.record(
            DisplayEvent(
                photo_id="hash-2",
                client_id="kitchen-dakboard",
                displayed_at=datetime(2026, 1, 2, tzinfo=UTC),
            )
        )

        events = repository.recent_for_client("kitchen-dakboard", limit=1)

        assert len(events) == 1
        assert events[0].photo_id == "hash-2"
    finally:
        database.close()
