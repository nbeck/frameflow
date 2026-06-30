from datetime import UTC, datetime
from pathlib import Path

import pytest

from frameflow.domain import DisplayEvent, Photo
from frameflow.rotation import RotationEngine

pytestmark = pytest.mark.unit


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


def test_duplicate_history_entries_use_newest_timestamp() -> None:
    # Regression: concurrent requests can insert the same photo_id multiple
    # times.  The policy must use the most recent displayed_at (not the oldest)
    # so that a photo shown many times is not incorrectly treated as stale.
    engine = RotationEngine()

    photos = [photo("a"), photo("b"), photo("c")]

    t1 = datetime(2026, 1, 1, 0, 0, 1, tzinfo=UTC)
    t2 = datetime(2026, 1, 1, 0, 0, 2, tzinfo=UTC)
    t3 = datetime(2026, 1, 1, 0, 0, 3, tzinfo=UTC)
    t4 = datetime(2026, 1, 1, 0, 0, 4, tzinfo=UTC)

    # photo "a" was shown four times (concurrent burst), most recently at t4.
    # photos "b" and "c" were shown once each at t2 and t3.
    # history arrives newest-first (as recent_for_client returns it).
    history = [
        DisplayEvent(photo_id="a", client_id="kitchen", displayed_at=t4),
        DisplayEvent(photo_id="c", client_id="kitchen", displayed_at=t3),
        DisplayEvent(photo_id="b", client_id="kitchen", displayed_at=t2),
        DisplayEvent(photo_id="a", client_id="kitchen", displayed_at=t1),
    ]

    selected = engine.next_photo(photos, history)

    # "b" was last shown at t2 — the oldest unique last-displayed timestamp.
    # If the policy mistakenly used t1 for "a", it would (incorrectly) pick "a".
    assert selected is not None
    assert selected.id == "b"
