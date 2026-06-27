# Security and Privacy Architecture

FrameFlow handles personal photos and provider credentials. Security and privacy must be designed from the start.

## Data sensitivity

Sensitive data includes:

- photo originals
- generated images
- provider credentials
- display tokens
- metadata such as timestamps and album names
- logs that may include file paths or provider identifiers

## Privacy defaults

- Do not send photos to third-party services unless a user explicitly configures a provider or processing plugin that requires it.
- Do not log secrets.
- Do not expose admin endpoints publicly by default.
- Prefer local network deployment for initial releases.
- Document all persistent data locations.

## Token model

Display URLs may require long-lived tokens because display clients often have limited authentication support. These tokens should be scoped to display delivery, not admin actions.

## Secrets

Secrets should be provided through environment variables, mounted secret files, or a local config mechanism. Secrets should never be committed.

## Remote access

Remote access is out of scope for the initial release. Users who expose FrameFlow outside their local network should place it behind a trusted reverse proxy and authentication layer until native admin auth is implemented.

## Logging

Logs should prioritize operational usefulness without leaking private data. Avoid logging full provider payloads, access tokens, or public delivery URLs with tokens.
