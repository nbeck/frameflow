# Background Workers

FrameFlow should keep expensive work outside display request paths.

## Worker responsibilities

Workers should handle:

- provider synchronization
- original downloads
- checksum calculation
- derivative generation
- stale derivative cleanup
- retention pruning
- health checks
- repair jobs

## Initial approach

The first implementation can use a simple in-process worker or scheduled job runner. The architecture should not require Celery, Redis, or a separate queue for Milestone 1.

The code should still isolate job orchestration from business logic so a future queue backend can be added.

## Job properties

Jobs should be:

- idempotent
- observable
- retryable where safe
- cancellable where practical
- recorded in the database

## Suggested job records

A job record should capture:

- job type
- status
- provider or display scope
- start timestamp
- end timestamp
- attempt count
- error classification
- summary counts

## Request path rule

Display delivery should never block on provider synchronization. If no eligible photo is available, the API should return a clear fallback response rather than starting a provider sync synchronously.
