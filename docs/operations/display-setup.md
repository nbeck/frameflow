# Display Client Setup

This guide covers configuring a display client (DAKboard or any HTTP-capable display) to receive photos from FrameFlow.

## Prerequisites

Before configuring a display client:

- FrameFlow is running and reachable from the display client's network
- At least one photo has been synchronized (`POST /sync` or background sync enabled)
- LAN binding is configured if the display client is on a different machine (see [Security Operations](security.md))

Verify FrameFlow is reachable from the display client's network:

```bash
curl http://<server-ip>:8000/health
# {"status":"ok"}
```

## Choosing a display ID

The `display_id` identifies a specific display client. FrameFlow uses it to maintain a separate rotation history per display, so each screen shows photos in its own sequence.

### Friendly names

Friendly names are readable and easy to reference in logs:

```
kitchen
office
bedroom
living-room
hallway-frame
```

Rules: letters, digits, hyphens, and underscores only; 1–64 characters. No spaces.

### UUID display IDs

UUIDs provide practical obscurity — useful when FrameFlow is accessible from outside your immediate LAN:

```bash
python3 -c "import uuid; print(uuid.uuid4())"
# e.g. f47ac10b-58cc-4372-a567-0e02b2c3d479
```

See [Security Operations](security.md) for the full guidance on when this matters.

### Recommendation

Use friendly names for home LAN deployments. Use UUIDs if FrameFlow is exposed beyond the local network.

## Validate the endpoint

Before configuring your display client, confirm the endpoint responds correctly:

```bash
curl -I http://<server-ip>:8000/displays/kitchen/photo
```

Expected response:

```
HTTP/1.1 200 OK
content-type: image/jpeg
cache-control: no-store, max-age=0
x-photo-id: <content-hash>
```

Save the photo to disk to confirm it is the correct image:

```bash
curl -o /tmp/test.jpg http://<server-ip>:8000/displays/kitchen/photo
open /tmp/test.jpg
```

Call the endpoint a second time. The `x-photo-id` header should change if there are multiple photos — the rotation is working.

## Configure DAKboard

### Photo URL block

In DAKboard, add a **Photo** or **Image** block and configure the URL to:

```
http://<server-ip>:8000/displays/<display_id>/photo
```

Examples:

```
http://192.168.1.10:8000/displays/kitchen/photo
http://192.168.1.10:8000/displays/office/photo
```

DAKboard fetches the URL on each refresh cycle and displays the returned image.

### Refresh interval

The refresh interval controls how often DAKboard re-fetches the URL. This directly controls how often the photo changes.

FrameFlow serves a new photo on every request — there is no server-side timer. **The refresh interval is your rotation cadence.**

Recommended values:

| Use case | Interval |
|---|---|
| Active display (office, kitchen) | 5–15 minutes |
| Background frame (hallway, bedroom) | 30–60 minutes |
| Slow slideshow feel | 2–4 hours |

FrameFlow returns `Cache-Control: no-store, max-age=0` on this endpoint, so DAKboard will always fetch a fresh image regardless of browser-level caching.

## Multi-display setup

Each display uses its own `display_id`. FrameFlow maintains an independent rotation history per display, so a photo shown on the kitchen display does not affect when the office display shows the same photo.

Example configuration for a three-display home:

| Display | display_id | URL |
|---|---|---|
| Kitchen | `kitchen` | `http://192.168.1.10:8000/displays/kitchen/photo` |
| Office | `office` | `http://192.168.1.10:8000/displays/office/photo` |
| Bedroom | `bedroom` | `http://192.168.1.10:8000/displays/bedroom/photo` |

All three can be configured simultaneously. Each will cycle through the full photo library independently.

## Troubleshooting

### 503 — No photos available

```json
{"detail": "No photos available."}
```

The photo library is empty or sync has not run. Trigger a sync:

```bash
curl -X POST http://<server-ip>:8000/sync
```

Then check the photo count:

```bash
curl http://<server-ip>:8000/status
# {"status":"ok","photo_count":42,...}
```

### 404 — Photo file not found

```json
{"detail": "Photo file not found."}
```

A photo is recorded in the database but the file is missing on disk. This can happen if files were moved or deleted without running a sync. Run `POST /sync` to reconcile the database with the current library.

### 422 — Invalid display_id

```json
{"detail":[{"msg":"...","type":"string_pattern_mismatch",...}]}
```

The `display_id` contains characters that are not allowed (e.g. a space, slash, or special character). Only letters, digits, hyphens, and underscores are permitted. Check the URL in your display client configuration.

### Cannot reach the server

Symptoms: DAKboard shows a broken image or the curl command times out.

1. Confirm FrameFlow is running: `curl http://127.0.0.1:8000/health` from the server itself.
2. Check `FRAMEFLOW_HOST`. If it is set to `127.0.0.1`, the server is not listening on the LAN interface. Change it to `0.0.0.0` and restart. See [Security Operations](security.md).
3. Confirm the server IP address. Use `ip addr` (Linux) or `ipconfig` (macOS/Windows) to find the LAN IP.
4. Check firewall rules on the server for port 8000.

### Photos not changing

The display shows the same photo on every refresh.

1. Confirm there is more than one photo: `curl http://<server-ip>:8000/status` → `photo_count` should be > 1.
2. Confirm the cache header on the display endpoint: `curl -I http://<server-ip>:8000/displays/<id>/photo` → should show `cache-control: no-store, max-age=0`.
3. Check the DAKboard refresh interval — if it is set very long (e.g. 24 hours), photos will appear static.
4. Confirm the `display_id` in the URL matches what you expect. Two displays using the same `display_id` share a rotation history and advance it together.

### display_id typos

If you misconfigure a `display_id` (e.g. `kitcen` instead of `kitchen`), FrameFlow will start a new independent rotation history under that ID. The endpoint will still return photos — there is no error. Check the `display_id` in your URL if rotation seems out of sync with another display.

## Manual validation checklist

The following steps require physical hardware and cannot be verified programmatically.

- [ ] DAKboard Photo block configured with `http://<server-ip>:8000/displays/<display_id>/photo`
- [ ] DAKboard loads and displays an image from FrameFlow (not a broken image placeholder)
- [ ] Image changes after the configured refresh interval elapses
- [ ] After N refresh cycles, photos rotate through the library without repetition before cycling back
- [ ] Multiple DAKboard panels configured with different `display_id` values show independent rotation sequences
- [ ] After stopping and restarting FrameFlow, rotation continues from where it left off (history is persisted in the database)
- [ ] If FrameFlow is unreachable, DAKboard shows its fallback behavior (broken image or last cached image — not a FrameFlow concern)
