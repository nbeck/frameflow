from datetime import UTC, datetime
from pathlib import Path

from frameflow.domain import DisplayEvent, Photo
from frameflow.rotation import RotationEngine


def photo(photo_id: str) -> Photo:
    return Photo(
        id=photo_id,
        library_id="family",
        source_path=Path(f"/photos/{photo_id}.jpg"),
    )


def test_empty_library_returns_none() -> None:
    engine = RotationEngine()

    assert engine.next_photo([], []) is None


def test_single_photo_is_returned() -> None:
    engine = RotationEngine()

    selected = engine.next_photo([photo("1")], [])

    assert selected is not None
    assert selected.id == "1"


def test_photo_never_displayed_is_preferred() -> None:
    engine = RotationEngine()

    photos = [
        photo("1"),
        photo("2"),
    ]

    history = [
        DisplayEvent(
            photo_id="1",
            client_id="kitchen",
            displayed_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
    ]

    selected = engine.next_photo(photos, history)

    assert selected is not None
    assert selected.id == "2"


def test_least_recently_displayed_photo_is_selected() -> None:
    engine = RotationEngine()

    photos = [
        photo("1"),
        photo("2"),
    ]

    history = [
        DisplayEvent(
            photo_id="1",
            client_id="kitchen",
            displayed_at=datetime(2026, 1, 2, tzinfo=UTC),
        ),
        DisplayEvent(
            photo_id="2",
            client_id="kitchen",
            displayed_at=datetime(2026, 1, 1, tzinfo=UTC),
        ),
    ]

    selected = engine.next_photo(photos, history)

    assert selected is not None
    assert selected.id == "2"


def test_selection_is_deterministic() -> None:
    engine = RotationEngine()

    photos = [
        photo("2"),
        photo("1"),
    ]

    selected = engine.next_photo(photos, [])

    assert selected is not None
    assert selected.id == "1"
