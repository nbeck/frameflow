from pathlib import Path

from frameflow.storage import get_schema_version, initialize_database


def test_initialize_database_creates_schema(tmp_path: Path) -> None:
    database_path = tmp_path / "frameflow.db"

    connection = initialize_database(database_path)

    try:
        assert database_path.exists()
        assert get_schema_version(connection) == 2
    finally:
        connection.close()
