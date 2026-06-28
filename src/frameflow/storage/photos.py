"""Photo repository."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from frameflow.domain import Photo


class PhotoRepository:
    """Repository for storing and retrieving photos."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def upsert(self, photo: Photo) -> None:
        """Insert or update a photo."""

        self._connection.execute(
            """
            INSERT INTO photos (
                library_id,
                source_path,
                content_hash,
                file_size,
                width,
                height,
                image_format,
                modified_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_path)
            DO UPDATE SET
                library_id = excluded.library_id,
                content_hash = excluded.content_hash,
                file_size = excluded.file_size,
                width = excluded.width,
                height = excluded.height,
                image_format = excluded.image_format,
                modified_at = excluded.modified_at,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                photo.library_id,
                str(photo.source_path),
                photo.content_hash,
                photo.file_size,
                photo.width,
                photo.height,
                photo.image_format,
                photo.modified_at.isoformat() if photo.modified_at else "",
            ),
        )

        self._connection.commit()

    def list_paths(self) -> set[Path]:
        """Return all stored photo source paths."""

        rows = self._connection.execute("SELECT source_path FROM photos").fetchall()

        return {Path(str(row[0])) for row in rows}

    def delete_missing(self, current_paths: set[Path]) -> int:
        """Delete photos whose source paths are not in the current path set."""

        existing_paths = self.list_paths()
        missing_paths = existing_paths - current_paths

        for path in missing_paths:
            self._connection.execute(
                "DELETE FROM photos WHERE source_path = ?",
                (str(path),),
            )

        self._connection.commit()

        return len(missing_paths)

    def count(self) -> int:
        """Return the number of stored photos."""

        row = self._connection.execute("SELECT COUNT(*) FROM photos").fetchone()

        assert row is not None

        return int(row[0])
