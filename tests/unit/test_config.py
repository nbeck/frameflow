from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from frameflow.api.app import app
from frameflow.config import ConfigurationError, Settings, load_settings, validate_settings


def test_default_settings() -> None:
    settings = Settings()

    assert settings.environment == "development"
    assert settings.host == "127.0.0.1"
    assert settings.port == 8000
    assert settings.data_dir == "data"
    assert settings.database_path == "data/frameflow.db"
    assert settings.photo_library == "photos"
    assert settings.log_level == "INFO"


def test_load_settings_returns_settings() -> None:
    settings = load_settings()

    assert isinstance(settings, Settings)


@pytest.mark.unit
def test_validate_settings_valid_config(tmp_path: Path) -> None:
    settings = Settings(
        photo_library=str(tmp_path),
        database_path=str(tmp_path / "db" / "frameflow.db"),
    )
    validate_settings(settings)


@pytest.mark.unit
def test_validate_settings_library_does_not_exist(tmp_path: Path) -> None:
    missing = tmp_path / "nonexistent"
    settings = Settings(photo_library=str(missing))

    with pytest.raises(ConfigurationError, match="does not exist"):
        validate_settings(settings)


@pytest.mark.unit
def test_validate_settings_library_is_a_file(tmp_path: Path) -> None:
    file_path = tmp_path / "not_a_dir.jpg"
    file_path.write_bytes(b"data")
    settings = Settings(photo_library=str(file_path))

    with pytest.raises(ConfigurationError, match="not a directory"):
        validate_settings(settings)


@pytest.mark.unit
def test_validate_settings_db_parent_is_a_file(tmp_path: Path) -> None:
    collision = tmp_path / "collision"
    collision.write_bytes(b"data")
    settings = Settings(
        photo_library=str(tmp_path),
        database_path=str(collision / "frameflow.db"),
    )

    with pytest.raises(ConfigurationError, match="not a directory"):
        validate_settings(settings)


@pytest.mark.unit
def test_validate_settings_db_parent_does_not_exist(tmp_path: Path) -> None:
    settings = Settings(
        photo_library=str(tmp_path),
        database_path=str(tmp_path / "new_dir" / "frameflow.db"),
    )
    validate_settings(settings)


@pytest.mark.unit
def test_validate_settings_db_parent_is_existing_directory(tmp_path: Path) -> None:
    db_dir = tmp_path / "data"
    db_dir.mkdir()
    settings = Settings(
        photo_library=str(tmp_path),
        database_path=str(db_dir / "frameflow.db"),
    )
    validate_settings(settings)


@pytest.mark.integration
def test_startup_raises_on_invalid_library(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bad_settings = Settings(
        photo_library=str(tmp_path / "nonexistent"),
        database_path=str(tmp_path / "frameflow.db"),
    )
    monkeypatch.setattr("frameflow.api.app.load_settings", lambda: bad_settings)

    with (
        pytest.raises(ConfigurationError, match="does not exist"),
        TestClient(app, raise_server_exceptions=True),
    ):
        pass
