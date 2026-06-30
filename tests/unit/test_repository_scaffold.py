# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

import frameflow


def test_repository_has_required_files() -> None:
    root = Path(__file__).resolve().parents[2]
    required_paths = [
        "README.md",
        "pyproject.toml",
        "docs",
        "adr",
        "mkdocs.yml",
        ".github/workflows/ci.yml",
    ]

    for required_path in required_paths:
        assert (root / required_path).exists()


def test_package_metadata_is_available() -> None:
    assert frameflow.__version__ == "1.0.0"
