# Testing Strategy

FrameFlow should have tests at several levels.

## Unit tests

Unit tests should cover domain logic, rotation scoring, storage path generation, provider reconciliation planning, and configuration validation.

## Integration tests

Integration tests should cover database repositories, Alembic migrations, file system operations, and API behavior.

## Contract tests

Provider contract tests should verify that each provider handles required lifecycle events consistently.

Minimum provider contract cases:

- empty provider library
- new asset discovered
- asset metadata updated
- asset removed upstream
- duplicate asset content
- failed original download
- retry after failure
- provider temporarily unavailable

## End-to-end tests

Later milestones should include Docker Compose based checks for sync, derivative generation, and display endpoint delivery.

## Test data

Test fixtures should use synthetic images and metadata only. Do not commit personal photos.

## Regression tests

Any bug that affects sync correctness, storage safety, or rotation repetition should receive a regression test.
