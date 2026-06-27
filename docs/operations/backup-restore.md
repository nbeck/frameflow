# Backup and Restore

## Backup goals

A backup should allow a user to restore FrameFlow without losing provider mappings, display history, or original assets.

## Minimum backup set

- database
- configuration
- originals
- provider credential recovery information

## Optional backup set

- generated derivatives
- thumbnails
- logs
- exports

## Restore process concept

1. Stop FrameFlow.
2. Restore database.
3. Restore configuration.
4. Restore originals.
5. Start FrameFlow.
6. Run storage verification.
7. Regenerate missing derivatives.
8. Run provider reconciliation.

## Verification

A restore is not complete until FrameFlow can verify database references against files on disk.
