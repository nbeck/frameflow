"""Photo repository."""

from __future__ import annotations

import sqlite3
from datetime import datetime
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
                modified_at,
                available
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(source_path)
            DO UPDATE SET
                library_id = excluded.library_id,
                content_hash = excluded.content_hash,
                file_size = excluded.file_size,
                width = excluded.width,
                height = excluded.height,
                image_format = excluded.image_format,
                modified_at = excluded.modified_at,
                available = 1,
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

    def get_by_id(self, photo_id: str) -> Photo | None:
        """Return a photo by its canonical domain ID (currently stored as content_hash)."""

        row = self._connection.execute(
            """
            SELECT
                library_id,
                source_path,
                content_hash,
                file_size,
                width,
                height,
                image_format,
                modified_at
            FROM photos
            WHERE content_hash = ?
            """,
            (photo_id,),
        ).fetchone()

        if row is None:
            return None

        content_hash = str(row[2])
        modified_at_value = str(row[7])

        return Photo(
            id=content_hash,
            library_id=str(row[0]),
            source_path=Path(str(row[1])),
            content_hash=content_hash,
            file_size=int(row[3]),
            width=int(row[4]),
            height=int(row[5]),
            image_format=str(row[6]),
            modified_at=(datetime.fromisoformat(modified_at_value) if modified_at_value else None),
        )

    def list_all(self) -> list[Photo]:
        """Return all available photos."""

        rows = self._connection.execute("""
            SELECT
                library_id,
                source_path,
                content_hash,
                file_size,
                width,
                height,
                image_format,
                modified_at
            FROM photos
            WHERE available = 1
            ORDER BY source_path
            """).fetchall()

        photos: list[Photo] = []
        for row in rows:
            content_hash = str(row[2])
            modified_at_value = str(row[7])
            photos.append(
                Photo(
                    id=content_hash,
                    library_id=str(row[0]),
                    source_path=Path(str(row[1])),
                    content_hash=content_hash,
                    file_size=int(row[3]),
                    width=int(row[4]),
                    height=int(row[5]),
                    image_format=str(row[6]),
                    modified_at=(
                        datetime.fromisoformat(modified_at_value) if modified_at_value else None
                    ),
                )
            )

        return photos

    def list_paths(self) -> set[Path]:
        """Return all stored photo source paths."""

        rows = self._connection.execute("SELECT source_path FROM photos").fetchall()

        return {Path(str(row[0])) for row in rows}

    def mark_unavailable(self, paths: set[Path]) -> int:
        """Mark photos at the given paths as unavailable.

        Returns the number of records updated.
        """

        if not paths:
            return 0

        updated = 0
        for path in paths:
            cursor = self._connection.execute(
                "UPDATE photos"
                " SET available = 0, updated_at = CURRENT_TIMESTAMP"
                " WHERE source_path = ?",
                (str(path),),
            )
            updated += cursor.rowcount

        self._connection.commit()

        return updated

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
