# 0007: Explainable rotation engine

## Status

Accepted

## Context

FrameFlow needs stable architectural boundaries before implementation begins.

## Decision

Rotation decisions must produce enough explanation data to debug why photos were selected or skipped.

## Consequences

The core value of FrameFlow is better rotation. Users need trust and visibility into that behavior.

This decision may introduce some up-front structure, but it reduces implementation drift as the project grows.
