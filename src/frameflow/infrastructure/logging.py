"""Centralized logging utilities for FrameFlow."""

from __future__ import annotations

import logging
import os
import sys

_LOGGING_CONFIGURED = False
_DEFAULT_LOG_LEVEL = "INFO"
_LOG_LEVEL_ENV_VAR = "FRAMEFLOW_LOG_LEVEL"


def configure_logging() -> None:
    """Configure application logging once."""

    global _LOGGING_CONFIGURED

    if _LOGGING_CONFIGURED:
        return

    log_level_name = os.getenv(_LOG_LEVEL_ENV_VAR, _DEFAULT_LOG_LEVEL).upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="timestamp=%(asctime)s level=%(levelname)s logger=%(name)s message=%(message)s",
        ),
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    _LOGGING_CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger."""

    configure_logging()
    return logging.getLogger(name)
