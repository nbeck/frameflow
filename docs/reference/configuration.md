# Configuration Reference

The final configuration format is not implemented yet. This page defines the intended configuration areas.

## Environment variables

Expected areas:

- application environment
- database URL
- data root
- log level
- admin access settings
- display token settings
- provider credentials

## Data root

FrameFlow should require a persistent data root. In Docker this is expected to be mounted as a volume.

## Database

Initial deployments should default to SQLite. PostgreSQL should be supported later through the same repository boundaries and migration discipline.

## Provider configuration

Provider configuration should be explicit and testable. A provider should not be considered enabled until credentials and required settings validate successfully.

## Display configuration

Each display should have:

- name
- enabled flag
- token
- target dimensions
- rotation policy
- allowed albums or sources

## Secrets

Secrets should not be stored in normal documentation, examples, or committed config files.
