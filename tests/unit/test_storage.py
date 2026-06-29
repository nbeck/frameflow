from pathlib import Path

from frameflow.storage import get_schema_version, initialize_database


def test_initialize_database_creates_schema(tmp_path: Path) -> None:
    database_path = tmp_path / "frameflow.db"

    connection = initialize_database(database_path)

    try:
        assert database_path.exists()
        assert get_schema_version(connection) == 4

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
