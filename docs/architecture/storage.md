# Storage Model

FrameFlow separates original assets from generated assets. This is a core architectural decision, not an implementation detail.

## Storage roots

A deployment should define a single data root. Under that root, FrameFlow owns predictable subdirectories.

```text
/frameflow-data/
├── originals/
├── generated/
├── thumbnails/
├── temp/
├── quarantine/
├── exports/
└── backups/
```

## Originals

Originals are provider-derived source files. They are immutable once accepted.

Rules:

- Never modify originals in place.
- Store originals using content-addressed or provider-stable paths.
- Record checksums in the database.
- Do not delete originals immediately when a provider removes a photo unless retention policy allows it.
- Treat original deletion as a lifecycle transition, not a casual cleanup.

## Generated assets

Generated assets include resized images, display-specific crops, thumbnails, previews, and future transcodes.

Rules:

- Generated assets must be stored outside `originals/`.
- Generated assets should be rebuildable.
- Derivative generation should be idempotent.
- Derivative records must point back to the source asset and transformation recipe.

## Temporary files

Downloads and transformations should first land in `temp/` and only move into final storage after validation.

Validation should include:

- file exists
- non-zero size
- expected media type
- checksum calculated
- image can be decoded
- database transaction can commit

## Quarantine

Files that download but fail validation should be moved to `quarantine/` with enough metadata to debug the problem. Quarantine should not block the entire sync run.

## Deletion strategy

Provider deletion does not necessarily mean immediate local deletion.

Recommended lifecycle:

1. Provider no longer reports asset.
2. Local asset marked `missing_upstream` or `deleted_upstream`.
3. Asset excluded from rotation by default.
4. Retention window passes.
5. Original and generated data become eligible for pruning.

## Backups

The minimum backup set is:

- database file
- configuration
- provider credentials or instructions to recreate them
- originals, unless the provider is considered authoritative and reliable

Generated assets can usually be excluded from backup if rebuild tooling is reliable.
