"""SQLite database initialization."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .migrations import set_schema_version
from .schema import SCHEMA_SQL


def initialize_database(path: Path) -> sqlite3.Connection:
    """Initialize and return a SQLite database connection."""

    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA_SQL)
    set_schema_version(connection)
    connection.commit()

    return connection
