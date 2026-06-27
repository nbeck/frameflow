# Data Model

FrameFlow uses a normalized domain model that separates provider identity, local asset identity, physical files, generated derivatives, displays, policies, and history.

This document describes the intended model. It is not a final migration specification.

## Core entities

### Provider

Represents a configured photo source.

Fields likely include:

- id
- provider type
- display name
- configuration reference
- enabled flag
- health state
- created timestamp
- updated timestamp

### Provider album

Represents an album, folder, shared album, or collection exposed by a provider.

Fields likely include:

- id
- provider id
- external album id
- title
- description
- visibility state
- sync cursor
- last seen timestamp

### Provider asset

Represents the provider-specific identity of a photo or video.

Fields likely include:

- id
- provider id
- provider album id
- external asset id
- external revision id
- provider checksum if available
- provider metadata hash
- last seen timestamp
- upstream lifecycle state

### Asset

Represents FrameFlow's normalized photo object.

Fields likely include:

- id
- media type
- captured timestamp
- imported timestamp
- content checksum
- perceptual hash when implemented
- width
- height
- orientation
- lifecycle state
- active flag

### Original file

Represents an immutable local original.

Fields likely include:

- id
- asset id
- storage path
- size bytes
- checksum
- media type
- accepted timestamp

### Generated asset

Represents a derivative generated from an original.

Fields likely include:

- id
- asset id
- recipe name
- width
- height
- format
- storage path
- checksum
- generated timestamp
- invalidated timestamp

### Display

Represents a configured display client.

Fields likely include:

- id
- name
- client type
- token hash
- target width
- target height
- enabled flag
- default rotation policy id

### Rotation policy

Represents selection rules for one or more displays.

Fields likely include:

- id
- name
- minimum repeat interval
- recency weight
- album diversity weight
- capture date diversity weight
- orientation rules
- exclusion rules

### Display event

Records what was served or skipped.

Fields likely include:

- id
- display id
- asset id
- generated asset id
- event type
- selected timestamp
- explanation summary
- policy version

## Important modeling rules

Provider identity and local asset identity are not the same thing. A provider asset can map to an existing local asset if the content checksum or reconciliation logic proves equivalence.

Albums are membership containers, not ownership boundaries. The same asset may appear in multiple albums.

Deletion is a lifecycle state. Avoid hard deletion until retention and recovery policies are explicit.

Generated assets are tied to recipes. When a recipe changes, old derivatives can be invalidated and regenerated.

## SQLite now, PostgreSQL later

The initial schema should avoid SQLite-only assumptions that make PostgreSQL migration difficult. Use explicit timestamps, clear foreign keys, migration discipline, and repository boundaries.
