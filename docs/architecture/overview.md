# Architecture Overview

FrameFlow is a self-hosted photo delivery platform that sits between photo providers and digital displays.

At a high level, FrameFlow has five major responsibilities:

1. Reconcile provider photo libraries into local database state.
2. Store immutable originals separately from generated derivatives.
3. Generate display-ready assets.
4. Select photos using an explainable rotation engine.
5. Serve selected photos through REST endpoints suitable for DAKboard and future clients.

## Conceptual architecture

```text
Photo Providers
  ├── Apple/iCloud Shared Album adapter (future)
  ├── Local folder adapter
  └── Additional provider plugins
        |
        v
Provider Reconciliation
        |
        v
Domain Database <----> Storage Manager
        |                  ├── originals/
        |                  ├── generated/
        |                  └── quarantine/
        v
Rotation Engine
        |
        v
REST API
        |
        v
Display Clients
  ├── DAKboard
  └── Future clients
```

## Core components

### API layer

The API layer exposes REST endpoints for health checks, library status, display feeds, asset delivery, and diagnostic explanations.

### Domain layer

The domain layer owns the language of the system: providers, albums, assets, displays, rotation policies, sync runs, generated assets, and display history.

### Provider layer

Providers expose external photo sources through a common contract. A provider adapter reports provider state and supports add, update, reconcile, and recover operations.

### Storage layer

The storage layer manages immutable originals, generated derivatives, quarantine files, temporary downloads, checksums, and path rules.

### Rotation layer

The rotation layer selects photos for displays using eligibility, scoring, diversity, recency, history, and optional policy constraints.

### Worker layer

The worker layer runs synchronization, derivative generation, cleanup, and maintenance jobs outside the request path.

## Initial deployment target

The initial deployment target is Docker Compose running on a Raspberry Pi or similar home server with external USB storage mounted into the container.

SQLite is the first database because it is simple, reliable, and appropriate for a single-node home deployment. The schema and repository boundaries must remain PostgreSQL-ready.
