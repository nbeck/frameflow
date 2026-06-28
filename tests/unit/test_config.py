from frameflow.config import Settings, load_settings


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
