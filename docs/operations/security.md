# Security Operations

See `SECURITY.md` for vulnerability reporting.

## Security posture

FrameFlow is designed for self-hosted, home LAN deployment. It assumes a trusted local network and provides no built-in authentication, authorization, or TLS termination in v1.1.

**What FrameFlow does not provide in v1.1:**

- User accounts or session management
- Authentication (API keys, bearer tokens, OAuth)
- Authorization (access control)
- Rate limiting
- HTTPS termination

These controls are the responsibility of the operator, either through network boundaries (LAN-only) or a reverse proxy (internet exposure).

## Threat model

FrameFlow is appropriate for:

- A home LAN where all connected devices are trusted
- A display client (e.g. DAKboard) polling for photos on the same network segment as the server

FrameFlow is **not** appropriate without additional controls for:

- Any interface reachable from the public internet
- Multi-tenant environments
- Networks where untrusted devices are present

## LAN binding

By default, FrameFlow binds to `127.0.0.1` (localhost only). This prevents any other device on the network from reaching it.

**Display clients on the local network require `FRAMEFLOW_HOST=0.0.0.0`** (or the server's specific LAN IP address, e.g. `192.168.1.10`).

In `.env`:

```env
FRAMEFLOW_HOST=0.0.0.0
FRAMEFLOW_PORT=8000
```

After changing this setting, restart FrameFlow. Verify with:

```bash
curl http://<server-lan-ip>:8000/health
```

> **Note:** `FRAMEFLOW_HOST` and `FRAMEFLOW_PORT` are read by the `uv run frameflow` startup command. They are ignored when invoking `uvicorn` directly — pass `--host` and `--port` manually in that case.

## Display ID security

FrameFlow does not authenticate display clients. Any client that can reach the server can request photos.

Using a UUID as the `display_id` provides practical obscurity: an attacker would need to guess a random 128-bit value. This is not a substitute for network-level access control, but it reduces casual exposure.

Generate a UUID display ID:

```bash
python3 -c "import uuid; print(uuid.uuid4())"
# e.g. f47ac10b-58cc-4372-a567-0e02b2c3d479
```

Configure your display client to call:

```
GET http://<server>:8000/displays/f47ac10b-58cc-4372-a567-0e02b2c3d479/photo
```

Treat this URL as a credential. Do not share it publicly.

## Internet exposure

If FrameFlow must be accessible over the internet, place it behind a reverse proxy with TLS and authentication. FrameFlow itself is not involved in this layer.

### nginx

```nginx
server {
    listen 443 ssl;
    server_name frameflow.example.com;

    ssl_certificate     /etc/ssl/certs/frameflow.crt;
    ssl_certificate_key /etc/ssl/private/frameflow.key;

    # Optional: restrict to known IPs
    # allow 203.0.113.0/24;
    # deny all;

    # Optional: HTTP Basic Auth
    # auth_basic "FrameFlow";
    # auth_basic_user_file /etc/nginx/.htpasswd;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Caddy

```caddyfile
frameflow.example.com {
    # Optional: restrict to known IPs
    # @blocked not remote_ip 203.0.113.0/24
    # respond @blocked 403

    # Optional: HTTP Basic Auth
    # basicauth {
    #     user $2a$14$...
    # }

    reverse_proxy 127.0.0.1:8000
}
```

When using a reverse proxy, keep FrameFlow bound to `127.0.0.1` (the default) so it is not directly reachable.
