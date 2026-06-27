# Photo Lifecycle

FrameFlow treats a photo as a lifecycle object, not just a file.

## States

Potential asset states:

- discovered
- downloading
- original_available
- generated_pending
- active
- hidden
- missing_upstream
- deleted_upstream
- quarantined
- prunable
- removed

## Happy path

```text
provider discovery
  -> provider asset record created
  -> original downloaded to temp
  -> original validated
  -> original moved to originals
  -> local asset created or linked
  -> derivative job queued
  -> display derivative generated
  -> asset eligible for rotation
```

## Provider deletion path

```text
asset previously active
  -> not seen during reconciliation
  -> marked missing_upstream
  -> excluded or deprioritized according to policy
  -> retention window passes
  -> marked prunable
  -> generated assets deleted
  -> original deleted only if policy allows
```

## Failed download path

```text
asset discovered
  -> download fails
  -> retry scheduled
  -> failure recorded
  -> sync continues
```

## Invalid file path

```text
file downloaded
  -> validation fails
  -> moved to quarantine
  -> provider asset marked failed
  -> sync run records data failure
```

## Recovery principle

A user should be able to retry sync or repair storage without manually editing the database.
