# Repository Layout

FrameFlow uses a documentation-first repository layout so implementation can proceed milestone by milestone.

```text
src/frameflow/api/        REST API boundary
src/frameflow/core/       domain models, policies, services
src/frameflow/db/         persistence and migrations
src/frameflow/providers/  provider adapters and contracts
src/frameflow/rotation/   rotation policies and selection
src/frameflow/storage/    storage paths and file operations
src/frameflow/workers/    jobs and orchestration
```

The current source directories intentionally contain package boundaries only. Application logic should be introduced through milestone PRs.

## Rule for new code

Every new module should map to one documented architecture area and one milestone.

## Avoid

- one large `utils.py`
- provider-specific logic inside API handlers
- storage path logic scattered across services
- rotation decisions without recorded explanations
- database schema changes without Alembic migrations
