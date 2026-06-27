# Roadmap

FrameFlow should be implemented in milestone order. Each milestone should leave the repository in a working state.

## Milestone 0: Repository Foundation

Status: in progress in this scaffold.

Scope:

- repository structure
- documentation
- governance
- CI
- Docker scaffolding
- Python tooling
- ADRs
- GitHub setup plan

## Milestone 1: Core Domain and Storage

Scope:

- core domain model
- SQLite schema
- Alembic migrations
- storage path rules
- immutable original file handling
- generated asset records

## Milestone 2: Provider Reconciliation

Scope:

- provider contract
- local folder provider
- sync runs
- reconciliation planning
- add, update, missing upstream, and recovery flows

## Milestone 3: Rotation Engine

Scope:

- display configuration
- rotation policy
- eligibility filters
- scoring
- display history
- explanations

## Milestone 4: DAKboard Delivery

Scope:

- DAKboard-compatible image endpoint
- display tokens
- display diagnostics
- setup guide

## Milestone 5: Operations and Hardening

Scope:

- backup and restore
- repair jobs
- observability
- security hardening
- release process

## Future directions

- additional provider plugins
- richer metadata analysis
- web admin UI
- multi-display coordination
- advanced rotation policies
- Home Assistant integration
