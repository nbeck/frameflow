# FrameFlow

FrameFlow is an open source, self-hosted photo delivery platform optimized for digital displays.

It is designed for people who manage always-on photo displays, including remote family displays, and need better control than typical cloud photo integrations provide. The first supported display client is DAKboard, but the architecture is REST-first so additional display clients can be added later.

## Project status

FrameFlow is in the repository-foundation phase. The repository intentionally includes architecture, governance, tooling, documentation, CI, and project planning before application implementation begins.

No production application code should be added until Milestone 1 is opened and accepted.

## Product principles

- Self-hosted by default
- Local-first and privacy-first
- Docker-first deployment
- REST-first integration model
- SQLite initially, PostgreSQL-ready by design
- Originals are immutable
- Generated data is stored separately from originals
- Provider synchronization is state reconciliation, not downloading
- Every provider must support add, update, reconcile, and recover flows
- Rotation decisions must be explainable
- Implementation should progress one milestone at a time

## What FrameFlow solves

Digital displays often repeat the same photos too frequently, especially when connected directly to shared cloud albums. FrameFlow acts as a controlled photo delivery layer between photo providers and displays.

FrameFlow will:

- ingest and reconcile photo libraries from providers
- preserve immutable originals
- generate display-ready derivatives separately
- track display history
- avoid excessive repetition
- expose simple REST endpoints for display clients
- explain why a photo was selected or skipped

## Repository map

```text
frameflow/
├── docs/                  # Product, architecture, operations, and implementation docs
├── adr/                   # Architecture Decision Records
├── src/frameflow/         # Python package skeleton only, no application code yet
├── tests/                 # Scaffold and future test suites
├── alembic/               # Database migration scaffolding
├── docker/                # Docker-related documentation and future assets
├── scripts/               # Developer workflow helpers
└── .github/               # GitHub Actions, issue templates, PR template, Dependabot
```

## Documentation starting points

- [Architecture overview](docs/architecture/overview.md)
- [System context](docs/architecture/system-context.md)
- [Synchronization model](docs/architecture/provider-sync.md)
- [Rotation engine](docs/architecture/rotation-engine.md)
- [Storage model](docs/architecture/storage.md)
- [Data model](docs/architecture/data-model.md)
- [Milestone plan](docs/roadmap/milestone-0-repository-foundation.md)
- [GitHub setup](GITHUB_SETUP.md)

## Development

FrameFlow uses Python, FastAPI, Docker, Ruff, Black, MyPy, Pytest, Alembic, and MkDocs.

```bash
make bootstrap
make check
```

The current repository scaffold is expected to pass formatting, linting, type checking, and tests once dependencies are installed.

## License

FrameFlow is licensed under the Apache License 2.0. See [LICENSE](LICENSE), [NOTICE](NOTICE), and [licenses/](licenses/).
