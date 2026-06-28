from datetime import UTC, datetime
from pathlib import Path

from frameflow.domain import DisplayEvent
from frameflow.history import RotationHistoryRepository
from frameflow.storage import initialize_database


def test_rotation_history_repository_records_event(tmp_path: Path) -> None:
    database = initialize_database(tmp_path / "frameflow.db")

    try:
        repository = RotationHistoryRepository(database)

        repository.record(
            DisplayEvent(
                photo_id="photo-1",
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
        repository = RotationHistoryRepository(database)

        older_event = DisplayEvent(
            photo_id="photo-1",
            client_id="kitchen-dakboard",
            displayed_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
        newer_event = DisplayEvent(
            photo_id="photo-2",
            client_id="kitchen-dakboard",
            displayed_at=datetime(2026, 1, 2, tzinfo=UTC),
        )
        other_client_event = DisplayEvent(
            photo_id="photo-3",
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
        repository = RotationHistoryRepository(database)

        repository.record(
            DisplayEvent(
                photo_id="photo-1",
                client_id="kitchen-dakboard",
                displayed_at=datetime(2026, 1, 1, tzinfo=UTC),
            )
        )
        repository.record(
            DisplayEvent(
                photo_id="photo-2",
                client_id="kitchen-dakboard",
                displayed_at=datetime(2026, 1, 2, tzinfo=UTC),
            )
        )

        events = repository.recent_for_client("kitchen-dakboard", limit=1)

        assert len(events) == 1
        assert events[0].photo_id == "photo-2"
    finally:
        database.close()
