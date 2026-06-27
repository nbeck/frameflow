#!/usr/bin/env bash
set -euo pipefail
ruff check src tests
ruff format --check src tests
black --check src tests
mypy src
pytest
