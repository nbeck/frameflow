# ADR-0002: SQLite First, PostgreSQL Ready

- Status: Accepted
- Date: 2026-06-27

## Context

The first deployment target is a simple self-hosted install, likely on a small server or Raspberry Pi. The architecture should not prevent future multi-user or higher-scale deployments.

## Decision

Use SQLite as the initial database and SQLAlchemy/Alembic in a way that keeps PostgreSQL viable later.

## Consequences

- Local installs remain simple.
- Database migrations are required from the beginning.
- PostgreSQL-specific features should be avoided until explicitly adopted.
