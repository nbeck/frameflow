# Provider Synchronization

Provider synchronization in FrameFlow is state reconciliation.

A provider sync run compares provider-reported state with local state, decides what changed, and applies explicit transitions. It is not a one-way download script.

## Why reconciliation matters

Photo providers can change in many ways:

- new photos are added
- photos are removed
- metadata changes
- albums are renamed
- photos move between albums
- provider APIs temporarily omit records
- downloads fail halfway
- credentials expire
- rate limits interrupt progress

A robust system must record what it saw, what it changed, what failed, and what should be retried.

## Sync phases

### 1. Start run

Create a sync run record with provider id, start timestamp, trigger type, and initial state.

### 2. Discover provider state

Fetch album and asset listings from the provider. This phase should be resumable where the provider supports cursors.

### 3. Compare

Compare provider records with local provider asset records.

Possible outcomes:

- new upstream asset
- known unchanged asset
- known asset with metadata change
- known asset with content revision change
- previously known asset not seen in current provider state
- provider album changed

### 4. Plan actions

Create a reconciliation plan before mutating files where practical.

Actions may include:

- create provider album record
- update album metadata
- create provider asset record
- download original
- link provider asset to existing local asset
- update metadata
- mark asset missing upstream
- retry failed download
- quarantine invalid file

### 5. Apply actions

Apply actions idempotently. File operations and database operations should be coordinated so partial failure can be recovered.

### 6. Finalize run

Record counts, failures, retryable items, non-retryable items, and final sync status.

## Required provider capabilities

Every provider must support these conceptual operations, even if the implementation is limited at first:

- add: discover and import new assets
- update: detect changed metadata or content revisions
- reconcile: compare full or cursor-based provider state against local state
- recover: resume or repair after partial failure

## Failure handling

Failures should be classified.

| Failure type | Example | Expected behavior |
| --- | --- | --- |
| transient | network timeout | retry later |
| credential | expired token | pause provider and require action |
| rate limit | provider throttling | back off |
| data | corrupt image | quarantine asset |
| invariant | duplicate impossible state | fail loudly and preserve evidence |

## Idempotency

Running the same sync twice should not duplicate assets, corrupt storage, or lose history.

Idempotency depends on:

- provider external ids
- content checksums
- stable storage paths
- unique constraints
- careful lifecycle state transitions
