# FrameFlow

FrameFlow is an open source, self-hosted photo delivery platform optimized for digital displays.

It is designed for people who manage always-on photo displays, including remote family displays, and need better control than typical cloud photo integrations provide. The first supported display client is DAKboard, but the architecture is REST-first so additional display clients can be added later.

## Project status

FrameFlow is approaching its first public release (v1.0.0). The core delivery pipeline — local library sync, SQLite persistence, rotation engine, and DAKboard-compatible REST endpoints — is implemented and tested.

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

FrameFlow:

- ingests and reconciles photo libraries from providers
- preserves immutable originals
- tracks display history per client
- avoids excessive repetition using a least-recently-displayed rotation policy
- exposes simple REST endpoints for display clients

## Repository map

```text
frameflow/
├── docs/                  # Product, architecture, operations, and implementation docs
├── adr/                   # Architecture Decision Records
├── src/frameflow/         # Python application package
├── tests/                 # Unit, integration, and contract test suites
├── alembic/               # Database migration scaffolding
└── .github/               # GitHub Actions, issue templates, PR template, Dependabot
```

## Development

### Prerequisites

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/) for dependency management
- [just](https://just.systems/) as the task runner

### Clone and set up

```bash
git clone https://github.com/nbeck/frameflow.git
cd frameflow
just setup
```

### Validate

```bash
just check
```

This runs Ruff, Black, MyPy, and Pytest with coverage.

### Run the server

```bash
cp .env.example .env   # edit as needed
uv run frameflow
```

The API will be available at `http://localhost:8000`. See [docs/operations.md](docs/operations.md) for the full configuration reference.

### Individual validation commands

```bash
uv run ruff check .
uv run black --check .
uv run mypy .
uv run pytest
```

## Docker

Build verification:

```bash
docker compose up --build
```

## Contributing

Before opening a pull request:

1. Create a feature branch from `main`.
2. Keep changes focused on a single issue.
3. Run `just check` and ensure all checks pass.
4. Ensure all GitHub Actions checks pass.
5. Squash merge after review.

## License

FrameFlow is licensed under the Apache License 2.0. See [LICENSE](LICENSE), [NOTICE](NOTICE), and [licenses/](licenses/).
