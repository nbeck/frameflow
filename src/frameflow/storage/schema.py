"""SQLite schema definitions for FrameFlow."""

SCHEMA_VERSION = 4

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_version (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    library_id TEXT NOT NULL,
    source_path TEXT NOT NULL UNIQUE,
    content_hash TEXT NOT NULL UNIQUE,
    file_size INTEGER NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    image_format TEXT NOT NULL,
    modified_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS photo_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    photo_id TEXT NOT NULL,
    displayed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    client_name TEXT NOT NULL,
    FOREIGN KEY(photo_id) REFERENCES photos(content_hash) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_photos_library_id
ON photos(library_id);

CREATE INDEX IF NOT EXISTS idx_photos_content_hash
ON photos(content_hash);

CREATE INDEX IF NOT EXISTS idx_photo_history_photo_id
ON photo_history(photo_id);

CREATE INDEX IF NOT EXISTS idx_photo_history_client_name
ON photo_history(client_name);

CREATE INDEX IF NOT EXISTS idx_photo_history_displayed_at
ON photo_history(displayed_at);
"""
