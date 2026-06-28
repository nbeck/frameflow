"""Rotation history repository."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from frameflow.domain import DisplayEvent


class RotationHistoryRepository:
    """Repository for recording and querying display history."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def record(self, event: DisplayEvent) -> None:
        """Record that a photo was displayed by a client."""

        self._connection.execute(
            """
            INSERT INTO photo_history (
                photo_id,
                client_name,
                displayed_at
            )
            VALUES (?, ?, ?)
            """,
            (
                event.photo_id,
                event.client_id,
                event.displayed_at.isoformat(),
            ),
        )

        self._connection.commit()

    def recent_for_client(self, client_id: str, limit: int = 100) -> list[DisplayEvent]:
        """Return recent display events for a client."""

        rows = self._connection.execute(
            """
            SELECT photo_id, client_name, displayed_at
            FROM photo_history
            WHERE client_name = ?
            ORDER BY displayed_at DESC
            LIMIT ?
            """,
            (client_id, limit),
        ).fetchall()

        return [
            DisplayEvent(
                photo_id=str(row[0]),
                client_id=str(row[1]),
                displayed_at=datetime.fromisoformat(str(row[2])),
            )
            for row in rows
        ]

    def count(self) -> int:
        """Return the number of stored display events."""

        row = self._connection.execute("SELECT COUNT(*) FROM photo_history").fetchone()

        assert row is not None

        return int(row[0])
