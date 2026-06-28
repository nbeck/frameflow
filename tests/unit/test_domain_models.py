from datetime import UTC, datetime
from pathlib import Path

from frameflow.domain import Album, Client, DisplayEvent, Library, Photo


def test_library_model() -> None:
    library = Library(id="library-1", name="Family Photos", root_path=Path("/photos"))

    assert library.id == "library-1"
    assert library.name == "Family Photos"
    assert library.root_path == Path("/photos")


def test_album_model() -> None:
    album = Album(id="album-1", library_id="library-1", name="Favorites")

    assert album.id == "album-1"
    assert album.library_id == "library-1"
    assert album.name == "Favorites"


def test_photo_model() -> None:
    modified_at = datetime(2026, 1, 1, tzinfo=UTC)

    photo = Photo(
        id="photo-1",
        library_id="library-1",
        source_path=Path("/photos/image.jpg"),
        content_hash="abc123",
        file_size=12345,
        width=4032,
        height=3024,
        image_format="JPEG",
        modified_at=modified_at,
    )

    assert photo.id == "photo-1"
    assert photo.library_id == "library-1"
    assert photo.source_path == Path("/photos/image.jpg")
    assert photo.content_hash == "abc123"
    assert photo.file_size == 12345
    assert photo.width == 4032
    assert photo.height == 3024
    assert photo.image_format == "JPEG"
    assert photo.modified_at == modified_at


def test_photo_model_allows_missing_content_hash() -> None:
    photo = Photo(
        id="photo-1",
        library_id="library-1",
        source_path=Path("/photos/image.jpg"),
    )

    assert photo.content_hash is None
    assert photo.file_size == 0
    assert photo.width == 0
    assert photo.height == 0
    assert photo.image_format == ""
    assert photo.modified_at is None


def test_client_model() -> None:
    client = Client(id="client-1", name="Kitchen DAKboard", client_type="dakboard")

    assert client.id == "client-1"
    assert client.name == "Kitchen DAKboard"
    assert client.client_type == "dakboard"


def test_display_event_model() -> None:
    displayed_at = datetime(2026, 1, 1, tzinfo=UTC)
    event = DisplayEvent(
        photo_id="photo-1",
        client_id="client-1",
        displayed_at=displayed_at,
    )

    assert event.photo_id == "photo-1"
    assert event.client_id == "client-1"
    assert event.displayed_at == displayed_at
