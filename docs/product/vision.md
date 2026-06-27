# Vision

FrameFlow should become the best self-hosted solution for serving photos to digital displays while avoiding repeated photos and providing intelligent, explainable rotation.

## Why this matters

Digital photo displays are most valuable when they feel fresh, personal, and low-maintenance. Existing cloud integrations often repeat a small subset of photos, provide limited control over rotation behavior, and make it hard to support displays owned by family members outside the home.

FrameFlow gives the owner a durable, self-hosted control layer. It stores a local, reconciled understanding of available photos, tracks what has been shown, prepares display-safe derivatives, and serves photos through simple endpoints that digital displays can consume.

## Target users

The first target user is a technical home user who manages multiple digital displays for family members. This user is comfortable running Docker on a Raspberry Pi, NAS, mini PC, or home server, but does not want to maintain a fragile custom script.

Future users include:

- families sharing photos across homes
- home automation enthusiasts
- DAKboard users who want better rotation
- self-hosted software users who prefer local control
- open source contributors interested in provider integrations

## Product promise

FrameFlow should make a digital display feel like it is pulling from a living, well-curated photo library without depending on a Mac, manual exports, or opaque cloud rotation.

## Non-goals for the initial product

- It is not a photo editing suite.
- It is not a replacement for Apple Photos, Google Photos, or iCloud.
- It is not a public social sharing platform.
- It is not a cloud service operated by the project maintainers.
- It is not initially optimized for multi-tenant commercial hosting.
