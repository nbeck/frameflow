"""Tests for centralized logging utilities."""

from __future__ import annotations

import logging

from pytest import MonkeyPatch

from frameflow.infrastructure import logging as frameflow_logging


def reset_logging_state() -> None:
    """Reset logging module state for isolated tests."""

    frameflow_logging._LOGGING_CONFIGURED = False

    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)


def test_get_logger_returns_logger() -> None:
    reset_logging_state()

    logger = frameflow_logging.get_logger("frameflow.test")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "frameflow.test"


def test_configure_logging_is_idempotent() -> None:
    reset_logging_state()

    frameflow_logging.configure_logging()
    frameflow_logging.configure_logging()

    root_logger = logging.getLogger()

    assert len(root_logger.handlers) == 1


def test_configure_logging_uses_default_info_level(
    monkeypatch: MonkeyPatch,
) -> None:
    reset_logging_state()
    monkeypatch.delenv("FRAMEFLOW_LOG_LEVEL", raising=False)

    frameflow_logging.configure_logging()

    assert logging.getLogger().level == logging.INFO


def test_configure_logging_uses_environment_log_level(
    monkeypatch: MonkeyPatch,
) -> None:
    reset_logging_state()
    monkeypatch.setenv("FRAMEFLOW_LOG_LEVEL", "DEBUG")

    frameflow_logging.configure_logging()

    assert logging.getLogger().level == logging.DEBUG
