"""Tests for FastAPI lifespan SyncLoop wiring."""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from frameflow.api.app import app
from frameflow.config import Settings


def _settings(sync_enabled: bool) -> Settings:
    return Settings(
        sync_enabled=sync_enabled,
        sync_interval_seconds=300,
        photo_library="/fake/photos",
        database_path="/fake/frameflow.db",
    )


@pytest.mark.integration
def test_lifespan_starts_sync_loop_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_loop = MagicMock()
    mock_loop_class = MagicMock(return_value=mock_loop)
    mock_scheduler = MagicMock()

    monkeypatch.setattr("frameflow.api.app.load_settings", lambda: _settings(sync_enabled=True))
    monkeypatch.setattr("frameflow.api.app.validate_settings", lambda s: None)
    monkeypatch.setattr("frameflow.api.app.get_database_connection", lambda: MagicMock())
    monkeypatch.setattr("frameflow.api.app.get_shared_scheduler", lambda s, c: mock_scheduler)
    monkeypatch.setattr("frameflow.api.app.SyncLoop", mock_loop_class)

    with TestClient(app):
        mock_loop_class.assert_called_once_with(scheduler=mock_scheduler, interval_seconds=300)
        mock_loop.start.assert_called_once()


@pytest.mark.integration
def test_lifespan_does_not_start_sync_loop_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_loop_class = MagicMock()

    monkeypatch.setattr("frameflow.api.app.load_settings", lambda: _settings(sync_enabled=False))
    monkeypatch.setattr("frameflow.api.app.validate_settings", lambda s: None)
    monkeypatch.setattr("frameflow.api.app.get_database_connection", lambda: MagicMock())
    monkeypatch.setattr("frameflow.api.app.get_shared_scheduler", lambda s, c: MagicMock())
    monkeypatch.setattr("frameflow.api.app.SyncLoop", mock_loop_class)

    with TestClient(app):
        mock_loop_class.assert_not_called()


@pytest.mark.integration
def test_lifespan_stops_sync_loop_on_shutdown(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_loop = MagicMock()
    mock_loop_class = MagicMock(return_value=mock_loop)

    monkeypatch.setattr("frameflow.api.app.load_settings", lambda: _settings(sync_enabled=True))
    monkeypatch.setattr("frameflow.api.app.validate_settings", lambda s: None)
    monkeypatch.setattr("frameflow.api.app.get_database_connection", lambda: MagicMock())
    monkeypatch.setattr("frameflow.api.app.get_shared_scheduler", lambda s, c: MagicMock())
    monkeypatch.setattr("frameflow.api.app.SyncLoop", mock_loop_class)

    with TestClient(app):
        mock_loop.stop.assert_not_called()

    mock_loop.stop.assert_called_once()
