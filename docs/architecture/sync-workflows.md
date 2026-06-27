# Synchronization Workflows

This document breaks provider reconciliation into concrete implementation workflows.

## New asset workflow

```text
provider lists external asset
  -> local provider asset does not exist
  -> create provider asset record
  -> download original to temp
  -> validate original
  -> calculate checksum
  -> create or link local asset
  -> move original to immutable storage
  -> queue derivative generation
  -> mark provider asset current
```

## Metadata update workflow

```text
provider lists known asset
  -> external revision or metadata hash changed
  -> update provider metadata snapshot
  -> update normalized fields if applicable
  -> preserve prior display history
  -> regenerate derivatives only if needed
```

## Upstream deletion workflow

```text
full reconciliation starts
  -> known provider asset not observed
  -> mark missing upstream
  -> exclude from default rotation
  -> keep original during retention window
  -> prune later if policy allows
```

## Recovery workflow

```text
sync fails mid-run
  -> sync run records partial failure
  -> completed file imports remain valid
  -> incomplete temp files are cleaned or retried
  -> next sync resumes from known local state
```

## Duplicate content workflow

```text
provider reports asset
  -> downloaded checksum matches existing asset
  -> create provider asset mapping to existing local asset
  -> do not store duplicate original unless policy requires it
  -> preserve album membership
```

## Invariants

- A provider asset may exist without a downloaded original during failure or pending states.
- A local asset should not become active until an original is validated.
- A display should not serve an asset without a valid derivative.
- A provider sync should never delete originals immediately by default.
