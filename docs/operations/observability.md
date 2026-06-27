# Observability

FrameFlow should be easy to troubleshoot from logs, health endpoints, and diagnostic pages.

## Health indicators

- API process alive
- database reachable
- data directory writable
- provider sync status
- derivative queue status
- display delivery success rate

## Sync metrics

Each sync run should report:

- discovered albums
- discovered assets
- new assets
- updated assets
- missing upstream assets
- failed downloads
- quarantined files
- retryable failures
- duration

## Rotation metrics

Each display should report:

- current asset
- last selected time
- eligible candidate count
- excluded candidate count
- repeat interval status
- last selection explanation

## Logs

Logs should include request ids and job ids where possible.
