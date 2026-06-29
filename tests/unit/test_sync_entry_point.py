"""Tests for the background synchronization entry point."""

import io
from pathlib import Path

import pytest
from PIL import Image

from frameflow.config import Settings
from frameflow.storage import PhotoRepository, initialize_database
from frameflow.workers import build_scan_scheduler

pytestmark = pytest.mark.unit


def _make_jpeg(path: Path, color: tuple[int, int, int] = (255, 0, 0)) -> None:
    buf = io.BytesIO()
    Image.new("RGB", (100, 100), color=color).save(buf, format="JPEG")
    path.write_bytes(buf.getvalue())


def test_sync_processes_photos_in_library(tmp_path: Path) -> None:
    library = tmp_path / "library"
    library.mkdir()
    _make_jpeg(library / "photo-1.jpg", color=(255, 0, 0))
    _make_jpeg(library / "photo-2.jpg", color=(0, 255, 0))

    database = initialize_database(tmp_path / "frameflow.db")
    try:
        settings = Settings(photo_library=str(library))
        scheduler = build_scan_scheduler(settings, database)

        processed = scheduler.run_once()

        assert processed == 2
        assert PhotoRepository(database).count() == 2
    finally:
        database.close()


def test_sync_is_idempotent(tmp_path: Path) -> None:
    library = tmp_path / "library"
    library.mkdir()
    _make_jpeg(library / "photo-1.jpg")

    database = initialize_database(tmp_path / "frameflow.db")
    try:
        settings = Settings(photo_library=str(library))
        scheduler = build_scan_scheduler(settings, database)

        scheduler.run_once()
        scheduler.run_once()

        assert PhotoRepository(database).count() == 1
    finally:
        database.close()


def test_sync_marks_deleted_photos_unavailable(tmp_path: Path) -> None:
    library = tmp_path / "library"
    library.mkdir()
    photo_path = library / "photo-1.jpg"
    _make_jpeg(photo_path)

    database = initialize_database(tmp_path / "frameflow.db")
    try:
        settings = Settings(photo_library=str(library))
        scheduler = build_scan_scheduler(settings, database)

        scheduler.run_once()
        assert PhotoRepository(database).count() == 1

        photo_path.unlink()
        scheduler.run_once()

        repo = PhotoRepository(database)
        assert repo.count() == 1
        assert repo.list_all() == []
    finally:
        database.close()
