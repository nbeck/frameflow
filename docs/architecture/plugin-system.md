# Plugin System

FrameFlow should support provider and client extensions without allowing plugins to leak implementation details into the core domain.

## Plugin types

### Provider plugins

Provider plugins connect FrameFlow to photo sources.

Examples:

- local folder provider
- Apple shared album provider
- Google Photos provider
- manual upload provider

### Delivery/client plugins

Delivery plugins adapt FrameFlow output to client-specific needs.

Examples:

- DAKboard image URL mode
- JSON feed mode
- future dashboard widgets

### Processing plugins

Processing plugins may later support custom derivative recipes, metadata enrichment, or image analysis.

## Provider contract

A provider plugin should expose capabilities for:

- configuration validation
- authentication status
- album discovery
- asset discovery
- original retrieval
- metadata retrieval
- cursor or full scan sync
- recovery from partial failure

## Core boundary

Plugins should translate external provider concepts into FrameFlow provider records. Core domain code should not know provider-specific API details.

## Versioning

Plugin interfaces should be versioned once external plugins are supported. Before then, internal adapters can evolve with ADRs documenting significant changes.

## Testing

Each provider must include contract tests that prove it handles:

- empty library
- new asset
- updated metadata
- removed upstream asset
- failed download
- retry after failure
- duplicate content
- provider outage
