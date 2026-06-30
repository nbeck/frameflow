# Changelog

All notable changes to FrameFlow will be documented in this file.

The format is based on Keep a Changelog, and this project intends to follow Semantic Versioning after the first public release.

## [Unreleased]

## [1.1.0] - 2026-06-30

### Added

- Display endpoint: `GET /displays/{display_id}/photo` serves photos to named display clients
  with per-display rotation history, `Cache-Control: no-store` headers, and `X-Photo-Id`
  response header. Display ID must match `[a-zA-Z0-9_-]{1,64}`.
- Cache-Control headers (`no-store, max-age=0`) added to all photo-serving endpoints.
- Operations: security posture guide covering LAN deployment, threat model, and reverse
  proxy configuration (`docs/operations/security.md`).
- Operations: DAKboard setup guide with display ID selection, curl validation, multi-display
  examples, and troubleshooting steps (`docs/operations/display-setup.md`).
- Architecture: DAKboard integration doc updated to reflect the implemented endpoint contract.
- ADR-0010: Display client architecture decision record.

### Fixed

- SQLite connection raised `ProgrammingError` when used from FastAPI's thread pool. Added
  `check_same_thread=False` to `initialize_database` so the shared connection works correctly
  across threads.
- Display endpoint always returned the same photo (lexicographically first hash). Two
  compounding bugs: (1) `LeastRecentlyDisplayedPolicy` dict comprehension used the oldest
  `displayed_at` for a repeated `photo_id` rather than the most recent, causing concurrently
  duplicated history entries to lock in a single photo permanently; (2) `PhotoService.
  get_next_photo` had no concurrency guard, allowing a TOCTOU race where concurrent requests
  all read empty history and selected the same photo. Fixed with a first-occurrence dict build
  and a module-level `threading.Lock`.

## [1.0.0] - 2026-06-29

### Added

- Local filesystem photo library provider with recursive discovery and hidden-file filtering.
- SHA-256 content hashing for stable photo identity across renames and moves.
- SQLite persistence with schema versioning and forward migrations.
- Photo availability tracking: files removed from disk are marked unavailable and restored automatically on reappearance.
- Least-recently-displayed rotation engine with per-client display history.
- REST API: `GET /health`, `GET /status`, `GET /config`, `POST /sync`, `GET /photos`, `GET /photos/next`, `GET /photos/{photo_id}/thumbnail`.
- Pydantic response models and accurate OpenAPI schema for all endpoints.
- Background scheduled sync loop with configurable interval and wait-first behavior.
- Manual sync endpoint with concurrency protection (409 on conflict).
- Structured stdout logging with key=value format and configurable log level.
- Operations runbook covering configuration, startup, sync, API reference, database, and logging.
- Release process documentation.
- Initial repository scaffold, documentation structure, governance and contribution files.
- CI on Python 3.12 and 3.13 (Ruff, Black, MyPy, Pytest).
