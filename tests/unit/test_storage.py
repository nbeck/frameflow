from pathlib import Path

from frameflow.storage import get_schema_version, initialize_database


def test_initialize_database_creates_schema(tmp_path: Path) -> None:
    database_path = tmp_path / "frameflow.db"

    connection = initialize_database(database_path)

    assert database_path.exists()
    assert get_schema_version(connection) == 1

    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }

    assert "schema_version" in tables
    assert "photos" in tables
    assert "photo_history" in tables
    connection.close()
