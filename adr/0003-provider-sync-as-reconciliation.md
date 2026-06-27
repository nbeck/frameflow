# ADR-0003: Treat Provider Sync as State Reconciliation

- Status: Accepted
- Date: 2026-06-27

## Context

Photo sources can change over time. Assets may be added, deleted, updated, moved, or temporarily unavailable. A download-only model cannot reliably represent provider truth.

## Decision

Provider synchronization will be modeled as state reconciliation. Every provider must support add, update, reconcile, and recover operations.

## Consequences

- Sync logic is more robust and auditable.
- Provider plugins must meet a higher contract.
- Interrupted syncs can be recovered intentionally.
