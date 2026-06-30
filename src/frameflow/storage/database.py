"""SQLite database initialization."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from frameflow.infrastructure.logging import get_logger

from .migrations import migrate, set_schema_version
from .schema import SCHEMA_SQL, SCHEMA_VERSION

_logger = get_logger("frameflow.storage")


def initialize_database(path: Path) -> sqlite3.Connection:
    """Initialize and return a SQLite database connection."""

    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path, check_same_thread=False)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA_SQL)
    migrate(connection)
    set_schema_version(connection)
    connection.commit()

    _logger.debug("Database ready at %s (schema v%d)", path, SCHEMA_VERSION)

    return connection
