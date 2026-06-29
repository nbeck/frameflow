"""System endpoint tests."""

from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from frameflow.api.app import app
from frameflow.api.dependencies import get_photo_service, get_settings, get_sync_state
from frameflow.config import Settings
from frameflow.domain import Photo
from frameflow.scanning import SyncState


class StubPhotoService:
    """Stub photo service for system endpoint tests."""

    def __init__(self, photos: list[Photo] | None = None) -> None:
        self._photos = photos or []

    def list_photos(self) -> list[Photo]:
        return self._photos

    def get_photo_by_id(self, photo_id: str) -> Photo | None:
        return None

    def get_next_photo(self, client_id: str) -> Photo | None:
        return None


def _make_photo(tmp_path: Path, n: int) -> Photo:
    path = tmp_path / f"photo-{n}.jpg"
    path.write_bytes(b"fake")
    return Photo(
        id=f"hash-{n}",
        library_id="default",
        source_path=path,
        content_hash=f"hash-{n}",
        file_size=4,
        width=100,
        height=100,
        image_format="JPEG",
        modified_at=datetime(2026, 1, n, tzinfo=UTC),
    )


def _override(settings: Settings | None = None, sync_state: SyncState | None = None) -> None:
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService()
    if settings is not None:
        app.dependency_overrides[get_settings] = lambda: settings
    if sync_state is not None:
        app.dependency_overrides[get_sync_state] = lambda: sync_state


def test_status_returns_expected_shape(tmp_path: Path) -> None:
    photos = [_make_photo(tmp_path, 1), _make_photo(tmp_path, 2)]
    settings = Settings(photo_library=str(tmp_path))
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService(photos)
    app.dependency_overrides[get_settings] = lambda: settings

    try:
        client = TestClient(app)
        response = client.get("/status")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["photo_count"] == 2
        assert "library_path" in body
        assert "library_exists" in body
        assert "last_sync_completed_at" in body
        assert "last_sync_photos_processed" in body
        assert "sync_running" in body
    finally:
        app.dependency_overrides.clear()


def test_status_library_exists_true_when_path_exists(tmp_path: Path) -> None:
    settings = Settings(photo_library=str(tmp_path))
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService()
    app.dependency_overrides[get_settings] = lambda: settings

    try:
        client = TestClient(app)
        response = client.get("/status")

        assert response.status_code == 200
        assert response.json()["library_exists"] is True
    finally:
        app.dependency_overrides.clear()


def test_status_library_exists_false_when_path_missing(tmp_path: Path) -> None:
    settings = Settings(photo_library=str(tmp_path / "nonexistent"))
    app.dependency_overrides[get_photo_service] = lambda: StubPhotoService()
    app.dependency_overrides[get_settings] = lambda: settings

    try:
        client = TestClient(app)
        response = client.get("/status")

        assert response.status_code == 200
        assert response.json()["library_exists"] is False
    finally:
        app.dependency_overrides.clear()


@pytest.mark.unit
def test_status_sync_fields_null_before_first_sync(tmp_path: Path) -> None:
    _override(settings=Settings(photo_library=str(tmp_path)), sync_state=SyncState())

    try:
        body = TestClient(app).get("/status").json()

        assert body["last_sync_completed_at"] is None
        assert body["last_sync_photos_processed"] is None
        assert body["sync_running"] is False
    finally:
        app.dependency_overrides.clear()


@pytest.mark.unit
def test_status_reflects_completed_sync(tmp_path: Path) -> None:
    completed_at = datetime(2026, 6, 29, 10, 0, 0, tzinfo=UTC)
    state = SyncState(
        last_sync_completed_at=completed_at,
        last_sync_photos_processed=42,
        sync_running=False,
    )
    _override(settings=Settings(photo_library=str(tmp_path)), sync_state=state)

    try:
        body = TestClient(app).get("/status").json()

        assert body["last_sync_completed_at"] == completed_at.isoformat()
        assert body["last_sync_photos_processed"] == 42
        assert body["sync_running"] is False
    finally:
        app.dependency_overrides.clear()


@pytest.mark.unit
def test_status_sync_running_true_while_syncing(tmp_path: Path) -> None:
    state = SyncState(sync_running=True)
    _override(settings=Settings(photo_library=str(tmp_path)), sync_state=state)

    try:
        body = TestClient(app).get("/status").json()

        assert body["sync_running"] is True
    finally:
        app.dependency_overrides.clear()


def test_config_returns_safe_fields() -> None:
    settings = Settings(
        photo_library="/photos",
        environment="development",
        log_level="INFO",
    )
    app.dependency_overrides[get_settings] = lambda: settings

    try:
        client = TestClient(app)
        response = client.get("/config")

        assert response.status_code == 200
        body = response.json()
        assert body["library_path"] == "/photos"
        assert body["environment"] == "development"
        assert body["log_level"] == "INFO"
        assert isinstance(body["supported_extensions"], list)
        assert ".jpg" in body["supported_extensions"]
    finally:
        app.dependency_overrides.clear()


def test_config_excludes_internal_runtime_fields() -> None:
    app.dependency_overrides[get_settings] = lambda: Settings()

    try:
        client = TestClient(app)
        response = client.get("/config")

        assert response.status_code == 200
        body = response.json()
        assert "database_path" not in body
        assert "host" not in body
        assert "port" not in body
    finally:
        app.dependency_overrides.clear()
