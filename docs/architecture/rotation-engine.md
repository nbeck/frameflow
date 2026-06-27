# Rotation Engine

The rotation engine chooses what a display should show next.

It must avoid excessive repetition, support multiple displays, and explain its decisions.

## Design goals

- Show fresh photos without ignoring older memories.
- Avoid showing the same photo too frequently.
- Avoid repeatedly selecting from the same small cluster.
- Respect display constraints such as orientation and derivative availability.
- Provide explanations for selected and skipped photos.
- Keep the algorithm simple enough to test and reason about.

## Selection pipeline

```text
Candidate pool
  -> eligibility filters
  -> scoring
  -> diversity adjustment
  -> tie breaking
  -> selection
  -> event recording
  -> explanation
```

## Eligibility filters

A photo may be ineligible because:

- it is inactive
- it was deleted or hidden upstream
- original file is missing
- required derivative is missing
- display orientation policy excludes it
- display has shown it too recently
- asset is quarantined
- policy explicitly excludes its album or tag

## Scoring factors

Initial scoring should be understandable and configurable.

Possible factors:

- time since last shown on this display
- time since last shown on any display
- album freshness
- capture date diversity
- import recency
- randomization seed
- manual boost or suppression in future

## Display history

Each served image should create a display event. The event should include the display, selected asset, generated asset, timestamp, policy version, and a compact explanation.

Display history is required for repetition avoidance.

## Explainability

FrameFlow should be able to answer:

- Why was this photo selected?
- Why was this other photo skipped?
- When was this photo last shown?
- Which policy affected the decision?
- Was the decision deterministic or random-weighted?

## First implementation strategy

Milestone 3 should implement a straightforward scoring algorithm before advanced intelligence.

Recommended first algorithm:

1. Filter to active assets with valid generated display asset.
2. Exclude assets shown within the minimum repeat interval.
3. Score by longest time since shown.
4. Add small seeded randomness to avoid rigid loops.
5. Record selection with explanation.

This creates immediate user value and establishes the history foundation for future improvements.
