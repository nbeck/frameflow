# 0005: REST-first delivery

## Status

Accepted

## Context

FrameFlow needs stable architectural boundaries before implementation begins.

## Decision

FrameFlow will expose display functionality through REST endpoints before implementing client-specific SDKs or proprietary integrations.

## Consequences

REST keeps DAKboard support simple and allows future clients to consume the same core capability.

This decision may introduce some up-front structure, but it reduces implementation drift as the project grows.
