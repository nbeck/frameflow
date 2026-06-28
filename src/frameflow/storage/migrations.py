"""Schema version management."""

from __future__ import annotations

import sqlite3

from .schema import SCHEMA_VERSION


def get_schema_version(connection: sqlite3.Connection) -> int:
    """Return the current schema version."""

    row = connection.execute("SELECT version FROM schema_version WHERE id = 1").fetchone()

    return 0 if row is None else int(row[0])


def set_schema_version(connection: sqlite3.Connection) -> None:
    """Record the current schema version."""

    connection.execute(
        """
        INSERT OR REPLACE INTO schema_version (id, version)
        VALUES (1, ?)
        """,
        (SCHEMA_VERSION,),
    )
