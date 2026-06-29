# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This project uses `uv` for package management and `just` as the task runner. The `justfile` is the canonical source for commands.

```bash
just setup      # install dependencies and set up pre-commit hooks
just test       # run pytest with coverage
just lint       # ruff + black check + mypy
just format     # auto-fix ruff and black
just check      # lint + test (full CI-equivalent)
just docs       # serve MkDocs locally
just docs-build # build strict MkDocs static site
just clean      # remove build artifacts and caches
```

Run a single test file:
```bash
uv run pytest tests/unit/test_photo_service.py
```

Run a single test by name:
```bash
uv run pytest -k "test_next_photo"
```

Run only unit or integration tests:
```bash
uv run pytest -m unit
uv run pytest -m integration
```

Start the API server:
```bash
uv run uvicorn frameflow.api.app:app --reload
```

## Architecture

FrameFlow is a self-hosted photo delivery platform. It syncs photos from providers (local filesystem today, cloud adapters later), stores them in a SQLite database, and serves them via a REST API to display clients like DAKboard.

### Layer map

| Package | Responsibility |
|---|---|
| `api/` | FastAPI app, route handlers, dependency wiring |
| `domain/` | Core dataclasses (`Photo`, `Album`, `Library`, `Client`, `DisplayEvent`) |
| `providers/` | `FileProvider` protocol + `LocalFileProvider` adapter; `FileCandidate` model |
| `scanning/` | `PhotoScanner` (orchestrates discovery) + `PhotoSynchronizer` (reconciles candidates into DB) |
| `metadata/` | `MetadataExtractor` — reads EXIF/image info from `FileCandidate` |
| `storage/` | `PhotoRepository` (SQLite CRUD), `schema.py` (raw SQL DDL), `migrations.py` (version tracking) |
| `history/` | `RotationHistoryRepository` — records `DisplayEvent` rows |
| `rotation/` | `RotationEngine` + `LeastRecentlyDisplayedPolicy` — picks next photo |
| `services/` | `PhotoService` (orchestrates get_next/list), `PhotoSelectionService` (bridges engine to service) |
| `config/` | `Settings` (pydantic-settings, `FRAMEFLOW_` env prefix), loaded via `load_settings()` |
| `infrastructure/` | Structured logging setup |
| `workers/` | Background job stubs (scanning scheduler lives in `scanning/scheduler.py`) |
| `clients/dakboard/` | DAKboard display client adapter (extensible pattern for future clients) |

### Request flow for `/photos/next`

```
GET /photos/next?client_id=X
  → photos route
  → PhotoService.get_next_photo(client_id)
    → PhotoRepository.list_all()
    → RotationHistoryRepository.recent_for_client(client_id)
    → PhotoSelectionService.next_photo(photos, history)
      → RotationEngine → LeastRecentlyDisplayedPolicy
    → RotationHistoryRepository.record(DisplayEvent)
  → FileResponse (serves file directly from source_path)
```

### Sync flow

```
PhotoScanner.scan()
  → FileProvider.discover() → Iterable[FileCandidate]
  → PhotoSynchronizer.sync(candidates)
    → MetadataExtractor.extract(candidate) → Photo
    → PhotoRepository.upsert(photo)
    → PhotoRepository.delete_missing(current_paths)  ← reconciliation step
```

### Dependency injection

`api/dependencies.py` wires everything together using FastAPI `Depends`. The database connection is a module-level `lru_cache` singleton (`sqlite3.Connection`). New dependencies should follow the same pattern.

### Configuration

All settings use the `FRAMEFLOW_` env prefix and load from `.env`. Copy `.env.example` to `.env` to get started. Key settings: `FRAMEFLOW_DATABASE_PATH`, `FRAMEFLOW_PHOTO_LIBRARY`, `FRAMEFLOW_LOG_LEVEL`.

### Database

SQLite is the current database. The schema is defined as raw SQL in `storage/schema.py` (`SCHEMA_SQL` + `SCHEMA_VERSION`). Alembic is present for future PostgreSQL migration readiness — avoid PostgreSQL-specific SQL until that transition is explicit. Every schema change requires bumping `SCHEMA_VERSION` and adding an Alembic migration.

### Originals are immutable

Original photo files are never modified. Generated derivatives (thumbnails, etc.) go to a separate path and can be regenerated. This is a hard rule (ADR-0004).

### Providers

New providers implement the `FileProvider` protocol (`providers/protocols.py`). Provider-specific logic must not leak into API handlers or services.

### ADRs

Architectural decisions are recorded in `adr/`. Write an ADR before implementing irreversible or high-impact changes.

## Development Workflow

### Core Principles

- Keep the architecture intentionally simple.
- Prefer the smallest production-quality implementation.
- Avoid unnecessary abstractions, frameworks, or refactors.
- Limit changes to the scope of the current GitHub issue.
- Follow existing project patterns whenever possible.

### Established Architectural Decisions

Treat these as settled unless explicitly told otherwise:

- `Photo.id` is the canonical domain identifier. For the current filesystem implementation, `Photo.id == content_hash`.
- SQLite `photos.id` is an internal surrogate key only.
- `source_path` is the synchronization/upsert key.
- API routes remain thin.
- `PhotoService` owns orchestration.
- Repository classes own persistence.
- Domain models live under `frameflow.domain`.
- Dependency wiring remains in `frameflow.api.dependencies`.

Do not re-investigate or redesign these decisions unless specifically requested.

### Phase 1 — Investigation

Before editing any files:

1. Read the GitHub issue.
2. Inspect all relevant source files.
3. Inspect related tests.
4. Produce a concise implementation plan including: files to modify, summary of proposed changes, architectural considerations, and anything intentionally left out of scope.

**Do not edit any files until the plan is approved.**

### Phase 2 — Implementation

After approval:

- Implement the smallest production-quality solution.
- Reuse existing project patterns.
- Avoid unrelated cleanup.
- Keep commits focused on the issue.
- Add or update tests where appropriate.

### Phase 3 — Validation

Run and iterate until all pass:

```bash
uv run ruff check .
uv run black --check .
uv run mypy .
uv run pytest
```

Fix failures automatically — do not ask the user to fix formatting or test failures manually.

### Phase 4 — Review Package

When implementation is complete, do not commit immediately. Provide:

- **Summary** — brief description of what changed
- **Files changed** — list every modified file
- **Tests added or updated** — summarize all test additions and changes
- **Validation** — Ruff, Black, MyPy, Pytest results
- **Git diff** — complete `git diff` output

**Wait for approval before committing.**

### Phase 5 — Commit

After approval:

- Stage only the intended files.
- Create the requested commit.
- Push the branch.
- Create the GitHub Pull Request.
- Wait for GitHub Actions to complete and report CI results.

**Do not merge the PR. Do not delete branches. Wait for approval before merging.**

### Architecture Review Gate

If an issue involves any of the following, perform an architecture review first and wait for approval before implementation:

- Domain models
- Repositories or persistence
- Synchronization
- API contracts
- Database schema
- Photo identity

## Testing

- **Markers**: `unit`, `integration`, `contract` — tag every test with one.
- **Coverage threshold**: 80% (enforced by `pytest --cov`).
- **Async**: `pytest-asyncio` is configured with `asyncio_mode = "auto"`.
- **Test data**: use synthetic images only; never commit personal photos.
- Provider contract tests must cover: empty library, new asset, metadata update, asset removed, duplicate content, download failure, retry, provider unavailable.
