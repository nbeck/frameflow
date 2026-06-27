# Development Standards

## Language and runtime

FrameFlow uses Python 3.12+.

## Formatting and linting

- Ruff for linting and import sorting
- Black-compatible formatting through Ruff or Black configuration
- MyPy for static type checking
- Pytest for tests
- Pre-commit for local enforcement

## Code expectations

- Prefer small modules with clear boundaries.
- Keep provider-specific code behind provider interfaces.
- Keep file system operations behind storage services.
- Keep database operations behind repositories or clearly scoped persistence modules.
- Include tests with every behavior change.
- Write ADRs for irreversible or high-impact decisions.

## Error handling

Use explicit error types for domain, provider, storage, and configuration failures. Avoid swallowing exceptions silently.

## Logging

Logs should be structured enough for troubleshooting. Do not log secrets or full tokenized URLs.

## Documentation

Every milestone should update documentation before or alongside implementation.
