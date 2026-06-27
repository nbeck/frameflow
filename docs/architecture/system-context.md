# System Context

FrameFlow is one system in a larger home photo-display environment.

## External actors

### Owner / administrator

The owner configures providers, manages displays, reviews sync health, and adjusts rotation policies.

### Display viewer

A display viewer sees photos on a DAKboard or future digital display. They do not interact with FrameFlow directly.

### Photo provider

A photo provider is an external or local source of photos. Examples include a local folder, an exported album, or a cloud shared album provider implemented later.

### Display client

A display client requests an image URL or feed from FrameFlow. DAKboard is the first supported client.

## External systems

### DAKboard

DAKboard can display images from web-accessible URLs. FrameFlow should expose a simple image endpoint and supporting feed endpoints that work within DAKboard constraints.

### File system / external storage

FrameFlow expects persistent storage. For home deployment this may be a USB hard drive attached to a Raspberry Pi.

### Provider APIs

Provider APIs may be unreliable, rate limited, or incomplete. FrameFlow must treat provider state as eventually consistent and recoverable.

## Trust boundaries

- Provider credentials cross the boundary between FrameFlow and external services.
- Photo originals cross from providers into local storage.
- Display endpoints may be accessible to local or remote displays.
- Admin endpoints must be protected before remote exposure is supported.

## Operating assumption

The first version is a single-node deployment controlled by one administrator. Multi-user hosted operation is explicitly out of scope for the initial milestones.
