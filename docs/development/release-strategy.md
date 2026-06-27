# Release Strategy

FrameFlow should use small, documented releases.

## Versioning

Use semantic versioning once the first public release is cut.

Before v1.0, minor versions may include breaking changes when documented.

## Release artifacts

A release should include:

- GitHub release notes
- changelog entry
- Docker image
- migration notes
- compatibility notes
- known limitations

## Release readiness checklist

- CI passing
- docs updated
- migrations tested
- Docker image builds
- upgrade notes written
- security notes reviewed
- sample configuration current

## First useful release

The first useful release should support a local folder provider, persistent SQLite state, derivative generation, a basic rotation engine, and DAKboard-compatible delivery endpoint.
