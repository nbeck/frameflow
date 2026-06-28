#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

print_step "Verifying required tools"
require_tool gh
require_tool git
require_github_auth

print_step "Bootstrap system is ready"
echo "Future steps will add labels, milestones, roadmap issue creation, and verification."
