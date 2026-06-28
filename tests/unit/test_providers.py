from datetime import datetime
from pathlib import Path

from frameflow.providers import FileCandidate


def test_file_candidate() -> None:
    candidate = FileCandidate(
        library_id="family",
        path=Path("/photos/image.jpg"),
        filename="image.jpg",
        size=12345,
        modified_at=datetime(2026, 1, 1),
    )

    assert candidate.library_id == "family"
    assert candidate.filename == "image.jpg"
    assert candidate.path == Path("/photos/image.jpg")
    assert candidate.size == 12345
