"""Photo endpoint tests."""

import io
from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from frameflow.api.app import app
from frameflow.api.dependencies import get_photo_service
from frameflow.domain import Photo


def _make_jpeg(path: Path) -> None:
    """Write a minimal valid JPEG to path."""
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    path.write_bytes(buf.getvalue())


class StubPhotoService:
    """Stub photo service for endpoint tests."""

    def __init__(
        self,
        photo: Photo | None = None,
        photos: list[Photo] | None = None,
        photo_by_id: Photo | None = None,
    ) -> None:
        self._photo = photo
        self._photos = photos or []
        self._photo_by_id = photo_by_id
        self.client_id: str | None = None

    def list_photos(self) -> list[Photo]:
        """Return configured photos."""

        return self._photos

    def get_photo_by_id(self, photo_id: str) -> Photo | None:
        """Return configured photo for ID lookup."""

        return self._photo_by_id

    def get_next_photo(self, client_id: str) -> Photo | None:
        """Return a configured photo."""

        self.client_id = client_id
        return self._photo


# --- Additional tests for /photos endpoint ---


def test_list_photos_returns_empty_list() -> None:
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(photos=[])

    try:
        client = TestClient(app)
        response = client.get("/photos")

        assert response.status_code == 200
        assert response.json() == []
    finally:
        app.dependency_overrides.clear()


def test_list_photos_returns_photo_metadata(tmp_path: Path) -> None:
    photo_path = tmp_path / "photo.jpg"
    photo_path.write_bytes(b"fake image data")

    photo = Photo(
        id="hash-1",
        library_id="default",
        source_path=photo_path,
        content_hash="hash-1",
        file_size=photo_path.stat().st_size,
        width=100,
        height=100,
        image_format="JPEG",
        modified_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(photos=[photo])

    try:
        client = TestClient(app)
        response = client.get("/photos")

        assert response.status_code == 200
        assert response.json() == [
            {
                "id": "hash-1",
                "source_path": str(photo_path),
            }
        ]
    finally:
        app.dependency_overrides.clear()


def test_list_photos_returns_multiple_photos(tmp_path: Path) -> None:
    photo_path_1 = tmp_path / "photo-1.jpg"
    photo_path_2 = tmp_path / "photo-2.jpg"
    photo_path_1.write_bytes(b"fake image data 1")
    photo_path_2.write_bytes(b"fake image data 2")

    photo_1 = Photo(
        id="hash-1",
        library_id="default",
        source_path=photo_path_1,
        content_hash="hash-1",
        file_size=photo_path_1.stat().st_size,
        width=100,
        height=100,
        image_format="JPEG",
        modified_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    photo_2 = Photo(
        id="hash-2",
        library_id="default",
        source_path=photo_path_2,
        content_hash="hash-2",
        file_size=photo_path_2.stat().st_size,
        width=200,
        height=200,
        image_format="JPEG",
        modified_at=datetime(2026, 1, 2, tzinfo=UTC),
    )
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(
        photos=[photo_1, photo_2]
    )

    try:
        client = TestClient(app)
        response = client.get("/photos")

        assert response.status_code == 200
        assert response.json() == [
            {
                "id": "hash-1",
                "source_path": str(photo_path_1),
            },
            {
                "id": "hash-2",
                "source_path": str(photo_path_2),
            },
        ]
    finally:
        app.dependency_overrides.clear()


def test_list_photos_does_not_expose_sqlite_surrogate_id(tmp_path: Path) -> None:
    photo_path = tmp_path / "photo.jpg"
    photo_path.write_bytes(b"fake image data")

    photo = Photo(
        id="hash-1",
        library_id="default",
        source_path=photo_path,
        content_hash="hash-1",
        file_size=photo_path.stat().st_size,
        width=100,
        height=100,
        image_format="JPEG",
        modified_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(photos=[photo])

    try:
        client = TestClient(app)
        response = client.get("/photos")

        assert response.status_code == 200
        assert "sqlite_id" not in response.json()[0]
        assert "database_id" not in response.json()[0]
        assert "content_hash" not in response.json()[0]
    finally:
        app.dependency_overrides.clear()


def test_next_photo_rejects_blank_client_id() -> None:
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService()

    try:
        client = TestClient(app)
        response = client.get("/photos/next", params={"client_id": ""})

        assert response.status_code == 422
        assert response.json()["detail"] == "client_id must not be blank."
    finally:
        app.dependency_overrides.clear()


def test_next_photo_rejects_whitespace_client_id() -> None:
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService()

    try:
        client = TestClient(app)
        response = client.get("/photos/next", params={"client_id": "   "})

        assert response.status_code == 422
        assert response.json()["detail"] == "client_id must not be blank."
    finally:
        app.dependency_overrides.clear()


def test_next_photo_returns_file(tmp_path: Path) -> None:
    photo_path = tmp_path / "photo.jpg"
    photo_path.write_bytes(b"fake image data")

    photo = Photo(
        id="hash-1",
        library_id="default",
        source_path=photo_path,
        content_hash="hash-1",
        file_size=photo_path.stat().st_size,
        width=100,
        height=100,
        image_format="JPEG",
        modified_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    service = StubPhotoService(photo)
    app.dependency_overrides[get_photo_service] = lambda: service

    try:
        client = TestClient(app)
        response = client.get("/photos/next", params={"client_id": "kitchen-dakboard"})

        assert response.status_code == 200
        assert response.content == b"fake image data"
        assert response.headers["content-type"] == "image/jpeg"
        assert response.headers["cache-control"] == "no-store"
        assert service.client_id == "kitchen-dakboard"
    finally:
        app.dependency_overrides.clear()


def test_next_photo_returns_not_found_when_no_photo() -> None:
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(None)

    try:
        client = TestClient(app)
        response = client.get("/photos/next", params={"client_id": "kitchen-dakboard"})

        assert response.status_code == 404
        assert response.json() == {"detail": "No photos available."}
    finally:
        app.dependency_overrides.clear()


def test_next_photo_returns_not_found_when_file_missing(tmp_path: Path) -> None:
    photo = Photo(
        id="hash-1",
        library_id="default",
        source_path=tmp_path / "missing.jpg",
        content_hash="hash-1",
        file_size=123,
        width=100,
        height=100,
        image_format="JPEG",
        modified_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(photo)

    try:
        client = TestClient(app)
        response = client.get("/photos/next", params={"client_id": "kitchen-dakboard"})

        assert response.status_code == 404
        assert response.json() == {"detail": "Photo file not found."}
    finally:
        app.dependency_overrides.clear()


# --- Thumbnail endpoint tests ---


def test_thumbnail_returns_image_response(tmp_path: Path) -> None:
    photo_path = tmp_path / "photo.jpg"
    _make_jpeg(photo_path)

    photo = Photo(
        id="hash-1",
        library_id="default",
        source_path=photo_path,
        content_hash="hash-1",
        file_size=photo_path.stat().st_size,
        width=100,
        height=100,
        image_format="JPEG",
        modified_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(photo_by_id=photo)

    try:
        client = TestClient(app)
        response = client.get("/photos/hash-1/thumbnail")

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"
        assert response.headers["cache-control"] == "public, max-age=86400, immutable"
        assert len(response.content) > 0
    finally:
        app.dependency_overrides.clear()


def test_thumbnail_returns_404_when_photo_not_found() -> None:
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(photo_by_id=None)

    try:
        client = TestClient(app)
        response = client.get("/photos/unknown-id/thumbnail")

        assert response.status_code == 404
        assert response.json() == {"detail": "Photo not found."}
    finally:
        app.dependency_overrides.clear()


def test_thumbnail_returns_404_when_file_missing(tmp_path: Path) -> None:
    photo = Photo(
        id="hash-1",
        library_id="default",
        source_path=tmp_path / "missing.jpg",
        content_hash="hash-1",
        file_size=123,
        width=100,
        height=100,
        image_format="JPEG",
        modified_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(photo_by_id=photo)

    try:
        client = TestClient(app)
        response = client.get("/photos/hash-1/thumbnail")

        assert response.status_code == 404
        assert response.json() == {"detail": "Photo file not found."}
    finally:
        app.dependency_overrides.clear()


def test_thumbnail_returns_500_when_image_is_corrupt(tmp_path: Path) -> None:
    photo_path = tmp_path / "corrupt.jpg"
    photo_path.write_bytes(b"this is not a valid image file")

    photo = Photo(
        id="hash-1",
        library_id="default",
        source_path=photo_path,
        content_hash="hash-1",
        file_size=photo_path.stat().st_size,
        width=100,
        height=100,
        image_format="JPEG",
        modified_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(photo_by_id=photo)

    try:
        client = TestClient(app)
        response = client.get("/photos/hash-1/thumbnail")

        assert response.status_code == 500
        assert response.json() == {"detail": "Thumbnail could not be generated."}
    finally:
        app.dependency_overrides.clear()
