# Product and Engineering Principles

## Local-first

FrameFlow should work well on a local network with local storage. External provider access may be required for synchronization, but day-to-day display delivery should not depend on provider uptime once assets are synchronized.

## Privacy-first

Photos are personal. FrameFlow should minimize data exposure, avoid unnecessary network calls, and make it clear where originals, derivatives, metadata, and credentials live.

## Originals are immutable

Original provider assets must not be modified in place. Any resize, crop, transcode, metadata extraction, or display-specific version belongs in generated storage.

## Generated data is disposable

Generated assets and derived metadata should be reproducible from originals and database state where possible. The system should make it safe to rebuild caches and derivatives.

## Synchronization is reconciliation

Provider sync is not simply downloading new files. Providers can add, update, delete, hide, reorder, rename, or temporarily fail to expose assets. FrameFlow must compare provider state with local state and take explicit actions.

## Rotation is explainable

A user should be able to understand why a photo was selected, skipped, suppressed, or delayed. Rotation should be deterministic enough to debug, while still supporting freshness and variety.

## REST-first

Display clients should only need simple HTTP access. DAKboard is first, but FrameFlow should avoid client-specific assumptions in core architecture.

## Docker-first

FrameFlow should be easy to run in Docker Compose on a Raspberry Pi, home server, mini PC, or NAS.

## Milestone-first delivery

Implementation should proceed in small, reviewable milestones. Each milestone should leave the repository in a working, tested state.
