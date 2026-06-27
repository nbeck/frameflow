# ADR-0004: Keep Originals Immutable and Generated Data Separate

- Status: Accepted
- Date: 2026-06-27

## Context

Users trust FrameFlow with personal photos. The system must not accidentally overwrite source assets or confuse generated derivatives with originals.

## Decision

Original assets are immutable. Generated data is always written to separate paths and can be regenerated.

## Consequences

- Data safety is prioritized.
- Storage layout is explicit.
- Cleanup and cache invalidation can operate on generated data without risking originals.
