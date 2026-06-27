#!/usr/bin/env bash
set -euo pipefail

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

echo "Configuring labels for $REPO"

# Delete GitHub defaults if present
for label in bug documentation duplicate enhancement "good first issue" "help wanted" invalid question wontfix; do
  gh label delete "$label" --repo "$REPO" --yes 2>/dev/null || true
done

create_label() {
  local name="$1"
  local color="$2"
  local description="$3"

  gh label create "$name" \
    --repo "$REPO" \
    --color "$color" \
    --description "$description" \
    2>/dev/null \
  || gh label edit "$name" \
    --repo "$REPO" \
    --color "$color" \
    --description "$description"
}

# Type
create_label "bug" "d73a4a" "Something is broken or behaving incorrectly"
create_label "feature" "a2eeef" "New product capability or user-facing behavior"
create_label "enhancement" "84b6eb" "Improvement to existing functionality"
create_label "documentation" "0075ca" "Documentation, examples, guides, or README changes"
create_label "refactor" "c5def5" "Code restructuring without intended behavior change"
create_label "performance" "fbca04" "Speed, memory, efficiency, or scalability improvement"
create_label "security" "b60205" "Security issue, hardening, or vulnerability-related work"
create_label "dependencies" "0366d6" "Dependency updates or dependency management"
create_label "testing" "5319e7" "Tests, coverage, fixtures, or validation"
create_label "ci" "0e8a16" "CI/CD, automation, GitHub Actions, or release workflows"

# Priority
create_label "priority: critical" "b60205" "Must be addressed immediately"
create_label "priority: high" "d93f0b" "Important and should be prioritized soon"
create_label "priority: medium" "fbca04" "Normal priority"
create_label "priority: low" "c2e0c6" "Useful but not urgent"

# Status
create_label "status: triage" "ededed" "Needs review, clarification, or prioritization"
create_label "status: ready" "0e8a16" "Ready to be worked on"
create_label "status: in progress" "1d76db" "Currently being worked on"
create_label "status: blocked" "b60205" "Blocked by another task, decision, or dependency"
create_label "status: review" "5319e7" "Needs review or validation"
create_label "status: waiting" "fbca04" "Waiting on external input or follow-up"
create_label "status: duplicate" "cccccc" "Duplicates another issue or pull request"

# Effort
create_label "effort: xs" "c2e0c6" "Very small change"
create_label "effort: s" "bfdadc" "Small change"
create_label "effort: m" "bfd4f2" "Medium-sized change"
create_label "effort: l" "d4c5f9" "Large change"
create_label "effort: xl" "f9d0c4" "Very large or multi-part change"

# Engineering areas
create_label "area: github" "0052cc" "GitHub repository settings, issues, discussions, or project management"
create_label "area: infrastructure" "0052cc" "Runtime, deployment, hosting, Docker, or environment setup"
create_label "area: documentation" "0052cc" "Project docs, guides, templates, or contributor materials"
create_label "area: testing" "0052cc" "Testing strategy, fixtures, validation, or quality gates"

# Product areas
create_label "area: ingestion" "1d76db" "Photo import, indexing, watching, or discovery"
create_label "area: metadata" "1d76db" "Photo metadata, EXIF, hashing, deduplication, or classification"
create_label "area: scheduler" "1d76db" "Rotation logic, recency rules, avoidance, or selection strategy"
create_label "area: storage" "1d76db" "Filesystem, database, cache, or backup behavior"
create_label "area: clients" "1d76db" "Display clients and integration surfaces"
create_label "area: dakboard" "1d76db" "DAKboard-specific behavior or compatibility"
create_label "area: api" "1d76db" "HTTP API, routes, contracts, or integration endpoints"
create_label "area: ui" "1d76db" "Admin UI, configuration UI, or visual interface"
create_label "area: sync" "1d76db" "Album sync, deletions, updates, or reconciliation"

# Community / resolution
create_label "good first issue" "7057ff" "Good for a first-time contributor"
create_label "help wanted" "008672" "Extra attention or outside contribution welcome"
create_label "question" "d876e3" "Question, discussion, or clarification"
create_label "invalid" "e4e669" "Not actionable or not applicable"
create_label "wontfix" "ffffff" "Intentionally not planned"
create_label "breaking change" "b60205" "Introduces a breaking change"

echo "Labels configured successfully."
