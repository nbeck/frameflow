# 0006: Plugin-oriented providers

## Status

Accepted

## Context

FrameFlow needs stable architectural boundaries before implementation begins.

## Decision

Provider integrations will be implemented behind contracts that keep provider API details out of the core domain.

## Consequences

This allows local folder, cloud album, and future providers to share reconciliation behavior.

This decision may introduce some up-front structure, but it reduces implementation drift as the project grows.
