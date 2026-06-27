# Security Policy

## Supported versions

FrameFlow has not reached its first release. Security fixes are handled on `main` until versioned releases begin.

## Reporting a vulnerability

Please do not open public issues for security vulnerabilities.

Report suspected vulnerabilities privately using GitHub Security Advisories when available, or contact the maintainers through the security contact listed in the repository profile.

## Security principles

- Local-first by default
- No telemetry by default
- No bundled user photos or credentials in tests
- Secrets must come from environment variables or secret stores
- Generated derivatives must not overwrite originals
