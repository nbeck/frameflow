#!/usr/bin/env bash
set -euo pipefail

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
MILESTONE="v0.1.0"

create_issue () {
    local TITLE="$1"
    local LABELS="$2"
    local BODY="$3"

    echo "Creating: $TITLE"

    gh issue create \
        --repo "$REPO" \
        --title "$TITLE" \
        --label "$LABELS" \
        --milestone "$MILESTONE" \
        --body "$BODY"
}

create_issue \
"Implement configuration system" \
"feature,area: infrastructure,priority: high,effort: m,status: ready" \
"Implement a typed configuration system using environment variables and sensible local defaults.

## Acceptance Criteria

- [ ] Environment-variable configuration
- [ ] Local development defaults
- [ ] Startup validation
- [ ] Configuration documentation"

create_issue \
"Create SQLite persistence layer" \
"feature,area: storage,priority: high,effort: l,status: ready" \
"Implement the initial persistence layer.

## Acceptance Criteria

- [ ] Database initialization
- [ ] Initial schema
- [ ] Schema version tracking
- [ ] Unit tests"

create_issue \
"Define core domain models" \
"feature,area: infrastructure,priority: high,effort: m,status: ready" \
"Define the application's core domain objects.

## Acceptance Criteria

- [ ] Library model
- [ ] Album model
- [ ] Photo model
- [ ] Client model
- [ ] Display event model"

create_issue \
"Add structured logging" \
"enhancement,area: infrastructure,priority: medium,effort: s,status: ready" \
"Add centralized structured logging throughout the application."

create_issue \
"Add health check endpoint" \
"feature,area: api,priority: medium,effort: s,status: ready" \
"Expose an API health endpoint for Docker and monitoring."

create_issue \
"Create Docker runtime" \
"feature,area: infrastructure,priority: high,effort: m,status: ready" \
"Create the production Docker image."

create_issue \
"Create Docker Compose development stack" \
"feature,area: infrastructure,priority: high,effort: m,status: ready" \
"Provide a Docker Compose environment for local development."

create_issue \
"Strengthen CI quality gates" \
"enhancement,area: github,area: testing,priority: high,effort: m,status: ready" \
"Expand GitHub Actions to enforce formatting, linting, typing, and testing."

create_issue \
"Document local development workflow" \
"documentation,area: documentation,priority: medium,effort: s,status: ready" \
"Document how contributors build, test, lint, and run FrameFlow."

echo
echo "Foundation roadmap created."
