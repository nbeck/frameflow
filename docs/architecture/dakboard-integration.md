# DAKboard Integration

DAKboard is the first supported display client for FrameFlow.

See ADR-0010 (`adr/0010-display-client-architecture.md`) for the architectural decisions that govern this integration.

## Integration model

FrameFlow provides DAKboard with a stable image URL that returns the next photo in rotation. DAKboard is configured with a **Photo URL block** pointing to:

```
GET /displays/{display_id}/photo
```

Example:

```
http://192.168.1.10:8000/displays/kitchen/photo
```

DAKboard fetches this URL on each configured refresh interval. FrameFlow returns the next photo from the rotation engine and records a display event in the rotation history. The endpoint is intentionally stateless from DAKboard's perspective — it fetches, receives an image, and displays it.

## Endpoint contract

| Property | Value |
|---|---|
| Method | `GET` |
| Path | `/displays/{display_id}/photo` |
| `display_id` format | `[a-zA-Z0-9_-]{1,64}` |
| Response (success) | `200` — image file in original format |
| `Cache-Control` | `no-store, max-age=0` |
| `X-Photo-Id` | Content hash of the served photo |
| Response (no photos) | `503` with `Retry-After: 300` |
| Response (file missing) | `404` |

`Cache-Control: no-store` ensures DAKboard (and intermediate caches) never reuse a previous response. The `X-Photo-Id` header allows the operator to identify which photo was served without inspecting the file.

## Rotation behavior

Each `display_id` maintains an independent rotation history. Two DAKboard panels configured with different display IDs (`kitchen`, `office`) advance their own sequences independently. There is no shared "current position" across displays.

The rotation policy is least-recently-displayed: FrameFlow prefers photos that have never been shown on that display, then falls back to the oldest-displayed photo by timestamp.

## DAKboard-specific considerations

**Refresh interval is the rotation cadence.** FrameFlow does not push photos to DAKboard; DAKboard polls. The refresh interval set in the DAKboard block directly controls how often the photo changes. See [Display Client Setup](../operations/display-setup.md) for recommended values.

**No DAKboard account API integration.** FrameFlow does not interact with the DAKboard platform API. It only serves photos over HTTP.

## Setup

For step-by-step configuration instructions, see [Display Client Setup](../operations/display-setup.md).

## Out of scope

The following items are not implemented and remain deferred:

- Full DAKboard account API integration (managing screens or layouts programmatically)
- Display-specific image derivatives (resolution or orientation per display)
- Server-side push or WebSocket delivery
- Native remote access (use a reverse proxy; see [Security Operations](../operations/security.md))
