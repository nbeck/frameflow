# API Design

FrameFlow is REST-first. The API should be simple enough for display clients, scripts, and home automation systems to use.

This document describes intended endpoint families, not final implementation.

## API principles

- Keep display delivery endpoints simple.
- Separate admin endpoints from public display endpoints.
- Use stable identifiers.
- Return machine-readable errors.
- Prefer explicit resource names over clever endpoints.
- Make diagnostics available without requiring database access.

## Endpoint families

### Health

```text
GET /health
GET /ready
GET /version
```

### Providers

```text
GET    /api/v1/providers
POST   /api/v1/providers
GET    /api/v1/providers/{provider_id}
PATCH  /api/v1/providers/{provider_id}
POST   /api/v1/providers/{provider_id}/sync
GET    /api/v1/providers/{provider_id}/sync-runs
```

### Albums and assets

```text
GET /api/v1/albums
GET /api/v1/albums/{album_id}
GET /api/v1/assets
GET /api/v1/assets/{asset_id}
GET /api/v1/assets/{asset_id}/history
```

### Displays

```text
GET    /api/v1/displays
POST   /api/v1/displays
GET    /api/v1/displays/{display_id}
PATCH  /api/v1/displays/{display_id}
GET    /api/v1/displays/{display_id}/next
GET    /api/v1/displays/{display_id}/current
```

### Delivery

```text
GET /d/{display_token}/next.jpg
GET /d/{display_token}/feed.json
GET /assets/{delivery_token}/{asset_variant}
```

Delivery endpoints should be easy to use from DAKboard custom image blocks.

### Diagnostics

```text
GET /api/v1/diagnostics/storage
GET /api/v1/diagnostics/sync
GET /api/v1/diagnostics/rotation/{display_id}
GET /api/v1/assets/{asset_id}/explain
```

## Authentication approach

Initial local-only development may use simple display tokens for delivery URLs and local admin access. Before remote exposure, admin authentication must be implemented.

Display tokens should be treated as secrets and stored hashed where possible.

## Response shape

Error responses should include:

- code
- message
- details when safe
- request id

Selection responses should include:

- asset id
- URL
- cache guidance
- explanation summary when requested
