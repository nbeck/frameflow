import sqlite3
from pathlib import Path

import pytest

from frameflow.storage import get_schema_version, initialize_database
from frameflow.storage.migrations import migrate

pytestmark = pytest.mark.unit


def test_initialize_database_creates_schema(tmp_path: Path) -> None:
    database_path = tmp_path / "frameflow.db"

    connection = initialize_database(database_path)

    try:
        assert database_path.exists()
        assert get_schema_version(connection) == 5

        foreign_keys_enabled = connection.execute("PRAGMA foreign_keys").fetchone()
        assert foreign_keys_enabled == (1,)

        indexes = {
            row[1]
            for row in connection.execute(
                "SELECT type, name FROM sqlite_master WHERE type = 'index'"
            ).fetchall()
        }

        assert "idx_photos_library_id" in indexes
        assert "idx_photos_content_hash" in indexes
        assert "idx_photo_history_photo_id" in indexes
        assert "idx_photo_history_client_name" in indexes
        assert "idx_photo_history_displayed_at" in indexes
    finally:
        connection.close()


_V4_PHOTOS_DDL = """
CREATE TABLE IF NOT EXISTS schema_version (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    version INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    library_id TEXT NOT NULL,
    source_path TEXT NOT NULL UNIQUE,
    content_hash TEXT NOT NULL UNIQUE,
    file_size INTEGER NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    image_format TEXT NOT NULL,
    modified_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def test_migrate_adds_available_column_to_v4_database(tmp_path: Path) -> None:
    connection = sqlite3.connect(tmp_path / "v4.db")
    connection.executescript(_V4_PHOTOS_DDL)
    connection.execute("INSERT OR REPLACE INTO schema_version (id, version) VALUES (1, 4)")
    connection.commit()

    assert get_schema_version(connection) == 4
    columns_before = {row[1] for row in connection.execute("PRAGMA table_info(photos)").fetchall()}
    assert "available" not in columns_before

    migrate(connection)

    columns_after = {row[1] for row in connection.execute("PRAGMA table_info(photos)").fetchall()}
    assert "available" in columns_after
    assert get_schema_version(connection) == 5
    connection.close()


def test_migrate_skips_fresh_database(tmp_path: Path) -> None:
    connection = initialize_database(tmp_path / "fresh.db")

    try:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(photos)").fetchall()}
        assert "available" in columns
        assert get_schema_version(connection) == 5
    finally:
        connection.close()
