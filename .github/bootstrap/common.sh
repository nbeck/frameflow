#!/usr/bin/env bash
set -euo pipefail

repo_name() {
  gh repo view --json nameWithOwner -q .nameWithOwner
}

require_tool() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required tool: $1"
    exit 1
  fi
}

require_github_auth() {
  gh auth status >/dev/null
}

print_step() {
  echo
  echo "==> $1"
}
