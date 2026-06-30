"""Display endpoint tests."""

import io
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from frameflow.api.app import app
from frameflow.api.dependencies import get_photo_service
from frameflow.domain import Photo

pytestmark = pytest.mark.unit


def _make_jpeg(path: Path) -> None:
    """Write a minimal valid JPEG to path."""
    img = Image.new("RGB", (100, 100), color=(0, 128, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    path.write_bytes(buf.getvalue())


def _photo(source_path: Path, photo_id: str = "hash-1") -> Photo:
    return Photo(
        id=photo_id,
        library_id="default",
        source_path=source_path,
        content_hash=photo_id,
        file_size=source_path.stat().st_size,
        width=100,
        height=100,
        image_format="JPEG",
        modified_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


class StubPhotoService:
    """Stub photo service for display endpoint tests."""

    def __init__(self, photo: Photo | None = None) -> None:
        self._photo = photo
        self.received_display_id: str | None = None

    def list_photos(self) -> list[Photo]:
        return []

    def get_photo_by_id(self, photo_id: str) -> Photo | None:
        return None

    def get_next_photo(self, client_id: str) -> Photo | None:
        self.received_display_id = client_id
        return self._photo


class RaisingPhotoService(StubPhotoService):
    """Stub that raises on get_next_photo."""

    def get_next_photo(self, client_id: str) -> Photo | None:
        raise RuntimeError("rotation engine exploded")


def test_display_photo_returns_200(tmp_path: Path) -> None:
    photo_path = tmp_path / "photo.jpg"
    _make_jpeg(photo_path)
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(_photo(photo_path))

    try:
        response = TestClient(app).get("/displays/kitchen/photo")
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()


def test_display_photo_content_type_is_image(tmp_path: Path) -> None:
    photo_path = tmp_path / "photo.jpg"
    _make_jpeg(photo_path)
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(_photo(photo_path))

    try:
        response = TestClient(app).get("/displays/kitchen/photo")
        assert response.headers["content-type"].startswith("image/")
    finally:
        app.dependency_overrides.clear()


def test_display_photo_has_cache_control_header(tmp_path: Path) -> None:
    photo_path = tmp_path / "photo.jpg"
    _make_jpeg(photo_path)
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(_photo(photo_path))

    try:
        response = TestClient(app).get("/displays/kitchen/photo")
        assert response.headers["cache-control"] == "no-store, max-age=0"
    finally:
        app.dependency_overrides.clear()


def test_display_photo_has_x_photo_id_header(tmp_path: Path) -> None:
    photo_path = tmp_path / "photo.jpg"
    _make_jpeg(photo_path)
    photo = _photo(photo_path, photo_id="abc123")
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(photo)

    try:
        response = TestClient(app).get("/displays/kitchen/photo")
        assert response.headers["x-photo-id"] == "abc123"
    finally:
        app.dependency_overrides.clear()


def test_display_photo_no_photos_returns_503() -> None:
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(None)

    try:
        response = TestClient(app).get("/displays/kitchen/photo")
        assert response.status_code == 503
        assert response.json() == {"detail": "No photos available."}
    finally:
        app.dependency_overrides.clear()


def test_display_photo_no_photos_has_retry_after_header() -> None:
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(None)

    try:
        response = TestClient(app).get("/displays/kitchen/photo")
        assert response.headers["retry-after"] == "300"
    finally:
        app.dependency_overrides.clear()


def test_display_photo_missing_file_returns_404(tmp_path: Path) -> None:
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
        response = TestClient(app).get("/displays/kitchen/photo")
        assert response.status_code == 404
        assert response.json() == {"detail": "Photo file not found."}
    finally:
        app.dependency_overrides.clear()


def test_display_photo_invalid_chars_returns_422() -> None:
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(None)

    try:
        # Space is not in [a-zA-Z0-9_-]
        response = TestClient(app).get("/displays/kitchen dakboard/photo")
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_display_photo_too_long_returns_422() -> None:
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(None)

    try:
        long_id = "a" * 65
        response = TestClient(app).get(f"/displays/{long_id}/photo")
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_display_photo_passes_display_id_to_service(tmp_path: Path) -> None:
    photo_path = tmp_path / "photo.jpg"
    _make_jpeg(photo_path)
    service = StubPhotoService(_photo(photo_path))
    app.dependency_overrides[get_photo_service] = lambda: service

    try:
        TestClient(app).get("/displays/bedroom-tv/photo")
        assert service.received_display_id == "bedroom-tv"
    finally:
        app.dependency_overrides.clear()


def test_display_photo_rotation_failure_returns_500() -> None:
    app.dependency_overrides[get_photo_service] = lambda: RaisingPhotoService()

    try:
        response = TestClient(app).get("/displays/kitchen/photo")
        assert response.status_code == 500
        assert response.json() == {"detail": "Photo rotation failed."}
    finally:
        app.dependency_overrides.clear()
