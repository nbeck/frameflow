# Changelog

All notable changes to FrameFlow will be documented in this file.

The format is based on Keep a Changelog, and this project intends to follow Semantic Versioning after the first public release.

## [Unreleased]

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
