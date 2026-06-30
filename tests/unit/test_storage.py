import sqlite3
import threading
from pathlib import Path

import pytest

from frameflow.api.dependencies import get_database_connection
from frameflow.config import Settings
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


def test_initialize_database_connection_is_usable_from_different_thread(
    tmp_path: Path,
) -> None:
    """Connection must not raise ProgrammingError when used across threads.

    FastAPI dispatches sync handlers in a thread pool, so the lru_cache
    singleton connection is always called from a different thread than the
    one that created it. check_same_thread=False is required.
    """
    connection = initialize_database(tmp_path / "threadtest.db")

    error: Exception | None = None

    def use_in_thread() -> None:
        nonlocal error
        try:
            connection.execute("SELECT 1").fetchone()
        except Exception as exc:
            error = exc

    t = threading.Thread(target=use_in_thread)
    t.start()
    t.join()

    connection.close()
    assert error is None, f"Cross-thread connection use raised: {error}"


def test_get_database_connection_initializes_schema_on_fresh_db(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """get_database_connection must apply the schema so requests succeed on a new installation."""
    db_path = tmp_path / "fresh.db"
    monkeypatch.setattr(
        "frameflow.api.dependencies.load_settings",
        lambda: Settings(database_path=str(db_path), photo_library=str(tmp_path)),
    )
    conn = None
    get_database_connection.cache_clear()
    try:
        conn = get_database_connection()
        assert get_schema_version(conn) == 5
        result = conn.execute("SELECT COUNT(*) FROM photos").fetchone()
        assert result == (0,)
    finally:
        if conn is not None:
            conn.close()
        get_database_connection.cache_clear()
