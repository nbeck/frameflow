# API Reference

The FrameFlow REST API is fully implemented as of v1.0.0.

The authoritative API reference — including all endpoint paths, request parameters, response schemas, status codes, and example responses — is in the [Operations Runbook](../operations.md#api-endpoints).

## Quick reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Process liveness check |
| `GET` | `/status` | Library path, photo count, and sync state |
| `GET` | `/config` | Active runtime configuration |
| `POST` | `/sync` | Trigger an immediate library sync |
| `GET` | `/photos` | List all available photos |
| `GET` | `/photos/next?client_id=<str>` | Serve the next photo for a display client |
| `GET` | `/photos/{photo_id}/thumbnail` | Serve a JPEG thumbnail |

All endpoints return JSON unless otherwise noted. `/photos/next` and `/photos/{photo_id}/thumbnail` return image files directly. No authentication is required.

See the [Operations Runbook](../operations.md#api-endpoints) for full request and response documentation.
