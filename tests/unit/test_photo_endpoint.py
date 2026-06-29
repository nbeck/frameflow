"""Photo endpoint tests."""

from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

from frameflow.api.app import app
from frameflow.api.dependencies import get_photo_service
from frameflow.domain import Photo


class StubPhotoService:
    """Stub photo service for endpoint tests."""

    def __init__(self, photo: Photo | None) -> None:
        self._photo = photo
        self.client_id: str | None = None

    def get_next_photo(self, client_id: str) -> Photo | None:
        """Return a configured photo."""

        self.client_id = client_id
        return self._photo


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
