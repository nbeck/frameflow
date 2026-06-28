from pathlib import Path

from frameflow.config import Settings, load_settings
from frameflow.config.models import PhotoLibrarySettings


def test_default_settings() -> None:
    settings = Settings()

    assert settings.environment == "development"
    assert settings.host == "127.0.0.1"
    assert settings.port == 8000
    assert settings.data_dir == "data"
    assert settings.database_path == "data/frameflow.db"
    assert settings.photo_library == "photos"
    assert settings.log_level == "INFO"


def test_default_photo_library_settings() -> None:
    settings = Settings()

    assert len(settings.photo_libraries) == 1

    library = settings.photo_libraries[0]
    assert library.id == "default"
    assert library.name == "Default Photo Library"
    assert library.type == "local"
    assert library.path == Path("photos")
    assert library.enabled is True


def test_custom_photo_library_settings() -> None:
    settings = Settings(
        photo_libraries=[
            PhotoLibrarySettings(
                id="family",
                name="Family Photos",
                path=Path("/photos/family"),
                enabled=True,
            ),
            PhotoLibrarySettings(
                id="archive",
                name="Archived Photos",
                path=Path("/photos/archive"),
                enabled=False,
            ),
        ]
    )

    assert len(settings.photo_libraries) == 2
    assert settings.photo_libraries[0].id == "family"
    assert settings.photo_libraries[0].name == "Family Photos"
    assert settings.photo_libraries[0].type == "local"
    assert settings.photo_libraries[0].path == Path("/photos/family")
    assert settings.photo_libraries[0].enabled is True

    assert settings.photo_libraries[1].id == "archive"
    assert settings.photo_libraries[1].enabled is False


def test_load_settings_returns_settings() -> None:
    settings = load_settings()

    assert isinstance(settings, Settings)
