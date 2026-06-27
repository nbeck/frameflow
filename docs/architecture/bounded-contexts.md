# Bounded Contexts

FrameFlow should be organized around stable product concepts, not framework folders alone.

## Provider context

Owns provider accounts, provider albums, provider assets, cursors, sync state, failures, and recovery flows.

Key questions:

- What does the provider currently expose?
- What changed since the last successful sync?
- Which local assets correspond to provider assets?
- Which failures are transient versus permanent?

## Library context

Owns the normalized local representation of photos, albums, metadata, lifecycle state, and relationships between provider objects and local assets.

Key questions:

- Which photos are available?
- Which albums or collections contain them?
- Which local files represent them?
- Are they active, deleted upstream, hidden, quarantined, or unavailable?

## Storage context

Owns physical file placement, original file immutability, generated derivative placement, checksums, and temporary files.

Key questions:

- Where should this file live?
- Has the content changed?
- Is the original safe and complete?
- Can generated data be rebuilt?

## Rotation context

Owns display eligibility, selection policies, scoring, display history, repetition controls, and explanations.

Key questions:

- Which photo should this display show next?
- Which photos are ineligible?
- Why was this photo selected?
- How do we avoid repeating the same people, album, time period, or asset too often?

## Delivery context

Owns REST endpoints, display tokens, image serving, cache headers, feed formats, and client compatibility.

Key questions:

- What does the client need right now?
- Is the requesting display allowed to access this feed?
- Which derivative is appropriate for this display?

## Operations context

Owns health checks, logs, diagnostics, backup guidance, migrations, and release management.
