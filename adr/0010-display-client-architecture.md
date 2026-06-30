# ADR-0010: Display Client Architecture

- Status: Accepted
- Date: 2026-06-29

## Context

FrameFlow v1.0.0 ships with `GET /photos/next?client_id=X`, which rotates and serves a photo for any string identifier. The endpoint works correctly at the service layer, but it was designed for programmatic API consumers. The first physical display — a DAKboard in the kitchen — needs a clean, stable URL it can embed directly in a configuration field with no query parameters.

The question is whether this feature should be designed specifically for DAKboard or as a generic display client capability. The `clients/` package was scaffolded at project start with an explicit extensibility intent. Per-client rotation history is already generic: `photo_history.client_name` is a plain string, and `RotationHistoryRepository.recent_for_client()` filters by it without any DAKboard-specific coupling.

## Decision

### Milestone name

The feature is named **Display Client Architecture**, not "DAKboard Integration". DAKboard is the first implementation of a generic pattern. No DAKboard-specific code belongs in the route or service layers.

### New endpoint

Add `GET /displays/{display_id}/photo` as the canonical display endpoint. This endpoint:

- Accepts `display_id` as a path parameter rather than a query parameter. Path parameters are correct for required identifiers that describe the resource being accessed; query parameters are for optional modifiers. This also makes the URL embeddable in any configuration field without requiring query string support.
- Delegates entirely to `PhotoService.get_next_photo(display_id)`, which already handles rotation, history recording, and file availability. No new service logic is required.
- Returns the photo as a direct `FileResponse` from `source_path`. No redirect, no JSON wrapper. A redirect adds a round-trip and display clients may cache the redirect target, defeating rotation.
- Sets `Cache-Control: no-store, max-age=0` on every response. Without this header, browsers and proxies may cache the image indefinitely and never trigger a rotation on subsequent fetches.
- Sets `X-Photo-Id` on the response to the served photo's `Photo.id`. This aids debugging without changing the response body or content type.

### Backward compatibility

`GET /photos/next?client_id=X` is part of the v1.0.0 API contract and is unchanged. Both endpoints coexist. `/photos/next` is kept for programmatic consumers; `/displays/{display_id}/photo` is the preferred URL for periodic display clients going forward.

### display_id conventions

`display_id` is validated with the path pattern `[a-zA-Z0-9_-]{1,64}`. FastAPI enforces this constraint automatically; invalid values receive a `422 Unprocessable Entity` response without reaching the service layer.

`display_id` is stored verbatim as `photo_history.client_name`. No schema change is required. The column already carries an index. A display is identified entirely by its `display_id` string; no `displays` table or explicit registration step exists. A display becomes known to the system on its first request.

### Display is not a persisted concept

There is no `displays` table in v1.1. Persisting displays as first-class entities would require schema changes, registration mechanics, and lifecycle management, none of which are justified by current requirements. If per-display configuration is needed in a future version — rotation policy, album filter, minimum display interval — the right first move is a `[display.kitchen]` section in settings, not a database table, unless the configuration must be mutable at runtime without a restart.

### Error responses

| Condition | Status | Notes |
|---|---|---|
| No photos in library | 503 Service Unavailable | Include `Retry-After: 300`. Distinguishes "service starting" from "resource not found". Sync may not have run yet. |
| Source file missing on disk | 404 Not Found | Marks the photo unavailable; subsequent calls will skip it. |
| Rotation engine raises an exception | 500 Internal Server Error | Caught at the route level; logged at ERROR with traceback. |
| `display_id` format invalid | 422 Unprocessable Entity | FastAPI path validation; no application code reached. |
| Unsupported image format | 200 (served as-is) | PIL does not re-encode originals during serving. Format validation belongs in the sync path, not the serve path. |

### Cache-Control on existing endpoints

As part of this work, all photo-serving endpoints are given explicit `Cache-Control` headers:

- `GET /displays/{display_id}/photo` → `no-store, max-age=0`
- `GET /photos/next` → `no-store`
- `GET /photos/{photo_id}/thumbnail` → `public, max-age=86400, immutable`

Thumbnails are content-addressed by `photo_id`. The same ID always yields the same bytes, so long-lived caching is safe.

### Logging

The display endpoint uses the same standard-library logger pattern as existing routes:

```python
_logger = get_logger("frameflow.api.display")
```

Log entries use the established `key=value` message style consistent with the existing formatter:

```
_logger.info("photo_served: display_id=%s photo_id=%s", display_id, photo.id)
_logger.warning("no_photos_available: display_id=%s", display_id)
_logger.error("rotation_failed: display_id=%s", display_id, exc_info=True)
```

No structured JSON logging is introduced. The existing logfmt-style formatter already makes log lines machine-parseable.

### Security posture

For v1.1, FrameFlow targets home LAN deployment. The threat model is a trusted home network. Mandatory authentication is not required.

The default `FRAMEFLOW_HOST=127.0.0.1` binds to localhost. A physical display on the LAN cannot reach a localhost-bound server. Operators must set `FRAMEFLOW_HOST=0.0.0.0` (or a specific LAN IP) in `.env` to make FrameFlow reachable from other devices.

Using a UUID as `display_id` makes the URL effectively unguessable, providing implicit security through obscurity:

```
http://192.168.1.42:8000/displays/f47ac10b-58cc-4372-a567-0e02b2c3d479/photo
```

This is sufficient for home use and is explicitly documented as such. Operators who expose FrameFlow outside their LAN should place it behind a reverse proxy (nginx or Caddy) with TLS and access controls. Bearer token support is deferred.

### Multi-display support

Multiple displays are already supported at the data layer. Each display uses a unique `display_id`; rotation histories are independent. No additional code is required. Two displays will never interfere with each other's rotation.

## Consequences

- `GET /displays/{display_id}/photo` is the canonical URL for all periodic display clients. DAKboard, tablets, kiosks, and browser slideshows can all use it.
- No schema changes. No new services. No new dependencies.
- `photo_history` continues to grow unbounded. At home scale (one display, hourly refresh) this produces roughly 8,760 rows per year — acceptable. History pruning remains deferred.
- Display clients have no per-display configuration in v1.1. Rotation policy and album filtering are the same for all displays.
- LAN binding is a manual operator step. This is the most likely first-time setup failure and must be prominent in the operations documentation.
- `GET /photos/next` remains available but is not the preferred endpoint for display clients going forward.
