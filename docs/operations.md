# Operations Runbook

This page is the primary operational guide for running FrameFlow locally in production.
Everything documented here reflects the current implementation.

---

## Prerequisites

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) for dependency management

Install dependencies:

```bash
uv sync
```

---

## Configuration

FrameFlow is configured entirely through environment variables with the `FRAMEFLOW_` prefix.
Variables are loaded from a `.env` file in the working directory and from the process environment.
Environment variables take precedence over `.env` values.

Copy the example file and edit it for your environment:

```bash
cp .env.example .env
```

### Settings reference

| Variable | Default | Description |
|---|---|---|
| `FRAMEFLOW_ENVIRONMENT` | `development` | Environment label (e.g. `production`) |
| `FRAMEFLOW_HOST` | `127.0.0.1` | Host address passed to uvicorn when starting via `uv run frameflow` |
| `FRAMEFLOW_PORT` | `8000` | Port passed to uvicorn when starting via `uv run frameflow` |
| `FRAMEFLOW_PHOTO_LIBRARY` | `photos` | Path to the photo library directory. **Must exist before startup.** |
| `FRAMEFLOW_DATABASE_PATH` | `data/frameflow.db` | Path to the SQLite database file. The parent directory is created automatically. |
| `FRAMEFLOW_LOG_LEVEL` | `INFO` | Python log level: `DEBUG`, `INFO`, `WARNING`, or `ERROR` |
| `FRAMEFLOW_SYNC_ENABLED` | `false` | Start the background scheduled sync loop on startup |
| `FRAMEFLOW_SYNC_INTERVAL_SECONDS` | `300` | Seconds between scheduled sync runs. Must be greater than 0. |

### Sample `.env` for local production

```bash
FRAMEFLOW_ENVIRONMENT=production
FRAMEFLOW_PHOTO_LIBRARY=/srv/photos
FRAMEFLOW_DATABASE_PATH=/srv/frameflow/frameflow.db
FRAMEFLOW_LOG_LEVEL=INFO
FRAMEFLOW_SYNC_ENABLED=true
FRAMEFLOW_SYNC_INTERVAL_SECONDS=300
```

### Known limitations

The following setting is defined in the `Settings` model but is not consumed at runtime:

| Variable | Default | Status |
|---|---|---|
| `FRAMEFLOW_DATA_DIR` | `data` | Defined in Settings but not consumed at runtime. Has no effect beyond establishing the default path for `FRAMEFLOW_DATABASE_PATH`. |

---

## Starting the server

The preferred startup command reads `FRAMEFLOW_HOST` and `FRAMEFLOW_PORT` from settings:

```bash
uv run frameflow
```

This is equivalent to running `python -m frameflow` with the package installed.

**Lower-level alternative** (bypasses `FRAMEFLOW_HOST` and `FRAMEFLOW_PORT` — host and port must
be supplied as CLI flags):

```bash
uv run uvicorn frameflow.api.app:app --host 127.0.0.1 --port 8000
```

For development with auto-reload (also bypasses settings for host/port):

```bash
uv run uvicorn frameflow.api.app:app --reload
```

### What happens at startup

1. Settings are loaded from `.env` and the environment.
2. Settings are validated — startup fails with `ConfigurationError` if `FRAMEFLOW_PHOTO_LIBRARY`
   does not exist or is not a directory.
3. The SQLite database is initialized: the schema is applied and any pending migrations are run.
   The database file and its parent directory are created automatically if they do not exist.
4. If `FRAMEFLOW_SYNC_ENABLED=true`, a background sync thread (`frameflow-sync-loop`) is started.
5. The API begins accepting requests.

On shutdown, the sync loop is signalled to stop and joined with a 5-second timeout.

---

## Photo library

Point `FRAMEFLOW_PHOTO_LIBRARY` at any directory on the local filesystem. FrameFlow
recursively scans it for image files.

**Supported formats:** `.jpg`, `.jpeg`, `.png`, `.webp`, `.heic`, `.heif` (case-insensitive)

**Skipped automatically:**
- Any file or directory whose path contains a component starting with `.` (hidden files)
- Non-file entries (directories, symlinks to directories)
- Files with unsupported extensions

Original files are never modified. FrameFlow only reads them.

---

## Synchronization

Sync reconciles the photo library on disk with the database.

### Manual sync

Trigger a single sync run immediately:

```bash
curl -X POST http://localhost:8000/sync
```

The request is synchronous — it blocks until the scan completes and returns the result:

```json
{
  "status": "ok",
  "photos_processed": 42,
  "sync_completed_at": "2026-06-29T12:00:00+00:00"
}
```

Returns `409 Conflict` if a sync is already in progress.

### Scheduled sync

Set `FRAMEFLOW_SYNC_ENABLED=true` to start an automatic background loop.
The loop **waits one full interval before its first run** — it does not sync immediately on startup.

```bash
FRAMEFLOW_SYNC_ENABLED=true
FRAMEFLOW_SYNC_INTERVAL_SECONDS=300   # 5 minutes
```

If a scheduled run starts while another sync is already running (e.g. triggered manually),
it is silently skipped and the loop continues on schedule.

### What sync does

1. Discovers all supported image files under `FRAMEFLOW_PHOTO_LIBRARY`.
2. Extracts metadata (dimensions, format, content hash) from each file.
3. Upserts each photo into the database (`source_path` is the upsert key).
4. Any file that raises an `OSError` during metadata extraction is skipped with a warning;
   the rest of the sync continues normally.
5. Files that were previously in the database but are no longer found on disk are marked
   `available=false`. They are retained in the database but excluded from photo rotation
   and the `/photos` listing. If the files reappear in a later sync, they are restored to
   available automatically.

---

## API endpoints

All endpoints return JSON unless otherwise noted. No authentication is required.

### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Returns `{"status": "ok"}`. Always succeeds while the process is alive. |

### System

| Method | Path | Description |
|---|---|---|
| `GET` | `/status` | Library path, existence, photo count, and current sync state |
| `GET` | `/config` | Active configuration: environment, log level, library path, supported extensions |
| `POST` | `/sync` | Trigger an immediate sync. Returns `409` if already running. |

#### `GET /status` example response

```json
{
  "status": "ok",
  "library_path": "/srv/photos",
  "library_exists": true,
  "photo_count": 312,
  "last_sync_completed_at": "2026-06-29T12:00:00+00:00",
  "last_sync_photos_processed": 312,
  "sync_running": false
}
```

`last_sync_completed_at` and `last_sync_photos_processed` are `null` until the first sync completes.
Sync state is in-memory and resets to `null` on process restart.

#### `GET /config` example response

```json
{
  "environment": "production",
  "log_level": "INFO",
  "library_path": "/srv/photos",
  "supported_extensions": [".heic", ".heif", ".jpeg", ".jpg", ".png", ".webp"]
}
```

### Photos

| Method | Path | Description |
|---|---|---|
| `GET` | `/photos` | List all available photos with `id`, `source_path`, and `content_hash` |
| `GET` | `/photos/next?client_id=<str>` | Serve the next photo file for a display client |
| `GET` | `/photos/{photo_id}/thumbnail` | Serve a 400×400 JPEG thumbnail |

#### `GET /photos/next`

`client_id` must be a non-blank string identifying the display client (e.g. a DAKboard instance
identifier). FrameFlow tracks display history per client to avoid repeating photos.

Returns the raw image file directly (not JSON) with the appropriate `Content-Type`.

**Error responses:**
- `422` — `client_id` is blank
- `404` — no available photos, or the source file is no longer on disk

#### `GET /photos/{photo_id}/thumbnail`

`photo_id` is the `content_hash` of the photo (returned by `GET /photos`).
Returns a JPEG image regardless of the original format.
Thumbnail dimensions are constrained to 400×400 pixels while preserving aspect ratio.

---

## Database

FrameFlow uses SQLite. The database file location is set by `FRAMEFLOW_DATABASE_PATH`
(default: `data/frameflow.db`).

The database is initialized automatically on startup — schema and migrations are applied before
the first request is served. Manual setup is not required.

**Current schema version:** 5

**Tables:**

| Table | Purpose |
|---|---|
| `photos` | One row per known photo file. `available=1` means the file was present in the last sync. |
| `photo_history` | One row per display event, keyed by `content_hash` and `client_name`. |
| `schema_version` | Single-row version tracker for migration management. |

### Backups

Back up the database file while FrameFlow is stopped, or use SQLite's online backup API
(`sqlite3 frameflow.db ".backup backup.db"`). The database is the only stateful artifact —
original photo files live in the library directory you control.

---

## Logging

Logs are written to **stdout** in key=value format:

```
timestamp=2026-06-29 12:00:00,000 level=INFO logger=frameflow.workers.sync message=Scheduled sync loop started (interval=300s)
```

Set `FRAMEFLOW_LOG_LEVEL=DEBUG` to see per-file sync activity.

### Key log events

| Logger | Level | Event |
|---|---|---|
| `frameflow.workers.sync` | `INFO` | Sync loop started, sync loop stopped, scheduled sync completed (with photo count) |
| `frameflow.workers.sync` | `DEBUG` | Scheduled sync skipped (another already running) |
| `frameflow.workers.sync` | `ERROR` | Scheduled sync failed (with traceback) |
| `frameflow.scanning.synchronizer` | `WARNING` | File skipped during sync due to read error (with traceback) |
