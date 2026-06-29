"""Tests for the application entry point."""

from unittest.mock import MagicMock, patch

import pytest

from frameflow.__main__ import main
from frameflow.config import Settings

pytestmark = pytest.mark.unit


def test_main_calls_uvicorn_with_default_host_and_port() -> None:
    settings = Settings(photo_library="/fake/photos")

    with (
        patch("frameflow.__main__.load_settings", return_value=settings),
        patch("frameflow.__main__.uvicorn.run") as mock_run,
    ):
        main()

    mock_run.assert_called_once_with(
        "frameflow.api.app:app",
        host="127.0.0.1",
        port=8000,
    )


def test_main_forwards_host_and_port_from_settings() -> None:
    settings = Settings(host="192.168.1.100", port=9000, photo_library="/fake/photos")

    with (
        patch("frameflow.__main__.load_settings", return_value=settings),
        patch("frameflow.__main__.uvicorn.run") as mock_run,
    ):
        main()

    mock_run.assert_called_once_with(
        "frameflow.api.app:app",
        host="192.168.1.100",
        port=9000,
    )


def test_main_passes_app_import_string() -> None:
    settings = Settings(photo_library="/fake/photos")
    mock_run = MagicMock()

    with (
        patch("frameflow.__main__.load_settings", return_value=settings),
        patch("frameflow.__main__.uvicorn.run", mock_run),
    ):
        main()

    assert mock_run.call_args[0][0] == "frameflow.api.app:app"
