# Deployment

FrameFlow is Docker-first.

## Initial deployment target

- Raspberry Pi 4 or 5, mini PC, NAS, or home server
- Docker and Docker Compose
- Persistent data directory mounted into the container
- SQLite database stored on persistent storage

## Storage mount

Example mount concept:

```text
/opt/frameflow/data -> /data
```

The container should treat `/data` as the persistent root for database, originals, generated assets, and logs where configured.

## Networking

Initial deployments should run on a trusted local network. Remote access should be handled by a reverse proxy and authentication layer until native remote access support is implemented.

## Backups

Back up:

- SQLite database
- configuration
- originals
- secrets or credential recovery process

Generated derivatives can be rebuilt, but backing them up may reduce recovery time.
