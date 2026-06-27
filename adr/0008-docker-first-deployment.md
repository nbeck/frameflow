# 0008: Docker-first deployment

## Status

Accepted

## Context

FrameFlow needs stable architectural boundaries before implementation begins.

## Decision

FrameFlow will optimize first for Docker Compose deployment on local home infrastructure.

## Consequences

The target user needs repeatable setup on Raspberry Pi, home server, mini PC, or NAS.

This decision may introduce some up-front structure, but it reduces implementation drift as the project grows.
