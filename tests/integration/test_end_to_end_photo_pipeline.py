"""API integration tests covering the Milestone 3 API surface."""

import io
from collections.abc import Generator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from frameflow.api.app import app
from frameflow.api.dependencies import get_photo_service, get_settings
from frameflow.config import Settings
from frameflow.domain import Photo
from frameflow.history import RotationHistoryRepository
from frameflow.rotation import RotationEngine
from frameflow.services import PhotoService
from frameflow.services.photo_selection import PhotoSelectionService
from frameflow.storage import PhotoRepository, initialize_database

pytestmark = pytest.mark.integration


@dataclass
class AppFixture:
    client: TestClient
    photos: list[Photo]
    history_repository: RotationHistoryRepository


def _make_jpeg(path: Path) -> None:
    img = Image.new("RGB", (100, 100), color=(128, 64, 32))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    path.write_bytes(buf.getvalue())


@pytest.fixture
def test_app(tmp_path: Path) -> Generator[AppFixture, None, None]:
    library = tmp_path / "library"
    library.mkdir()

    photos: list[Photo] = []
    for i in range(1, 4):
        path = library / f"photo-{i}.jpg"
        _make_jpeg(path)
        photo = Photo(
            id=f"hash-{i}",
            library_id="default",
            source_path=path,
            content_hash=f"hash-{i}",
            file_size=path.stat().st_size,
            width=100,
            height=100,
            image_format="JPEG",
            modified_at=datetime(2026, 1, i, tzinfo=UTC),
        )
        photos.append(photo)

    db_path = tmp_path / "frameflow.db"
    database = initialize_database(db_path)

    photo_repository = PhotoRepository(database)
    history_repository = RotationHistoryRepository(database)

    for photo in photos:
        photo_repository.upsert(photo)

    service = PhotoService(
        photo_repository=photo_repository,
        history_repository=history_repository,
        selection_service=PhotoSelectionService(RotationEngine()),
    )
    settings = Settings(photo_library=str(library))

    app.dependency_overrides[get_photo_service] = lambda: service
    app.dependency_overrides[get_settings] = lambda: settings

    yield AppFixture(
        client=TestClient(app),
        photos=photos,
        history_repository=history_repository,
    )

    app.dependency_overrides.clear()
    database.close()


def test_list_photos_returns_all_seeded_photos(test_app: AppFixture) -> None:
    response = test_app.client.get("/photos")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    for item in body:
        assert "id" in item
        assert "source_path" in item
        assert "content_hash" not in item


def test_next_photo_serves_image_file(test_app: AppFixture) -> None:
    response = test_app.client.get("/photos/next", params={"client_id": "client-a"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")
    assert len(response.content) > 0


def test_next_photo_rejects_blank_client_id(test_app: AppFixture) -> None:
    response = test_app.client.get("/photos/next", params={"client_id": ""})

    assert response.status_code == 422
    assert response.json()["detail"] == "client_id must not be blank."


def test_thumbnail_returns_jpeg_for_known_photo(test_app: AppFixture) -> None:
    photo_id = test_app.photos[0].id
    response = test_app.client.get(f"/photos/{photo_id}/thumbnail")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert len(response.content) > 0


def test_thumbnail_returns_404_for_unknown_id(test_app: AppFixture) -> None:
    response = test_app.client.get("/photos/does-not-exist/thumbnail")

    assert response.status_code == 404


def test_status_reports_correct_photo_count(test_app: AppFixture) -> None:
    response = test_app.client.get("/status")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["photo_count"] == 3
    assert body["library_exists"] is True


def test_config_returns_supported_extensions(test_app: AppFixture) -> None:
    response = test_app.client.get("/config")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["supported_extensions"], list)
    assert ".jpg" in body["supported_extensions"]


def test_rotation_is_independent_per_client(test_app: AppFixture) -> None:
    response_a = test_app.client.get("/photos/next", params={"client_id": "client-a"})
    response_b = test_app.client.get("/photos/next", params={"client_id": "client-b"})

    assert response_a.status_code == 200
    assert response_b.status_code == 200

    history_a = test_app.history_repository.recent_for_client("client-a")
    history_b = test_app.history_repository.recent_for_client("client-b")

    assert len(history_a) == 1
    assert all(e.client_id == "client-a" for e in history_a)
    assert len(history_b) == 1
    assert all(e.client_id == "client-b" for e in history_b)


def test_display_photo_returns_image(test_app: AppFixture) -> None:
    response = test_app.client.get("/displays/kitchen/photo")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")
    assert len(response.content) > 0


def test_display_photo_records_display_id_in_history(test_app: AppFixture) -> None:
    test_app.client.get("/displays/kitchen/photo")

    history = test_app.history_repository.recent_for_client("kitchen")
    assert len(history) == 1
    assert history[0].client_id == "kitchen"
