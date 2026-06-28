from pathlib import Path

from frameflow.domain import Photo
from frameflow.services.photo_selection import PhotoSelectionService


def test_photo_selection_service_returns_photo() -> None:
    service = PhotoSelectionService()

    photos = [
        Photo(
            id="1",
            library_id="family",
            source_path=Path("/photos/1.jpg"),
        )
    ]

    selected = service.next_photo(photos, [])

    assert selected is not None
    assert selected.id == "1"
