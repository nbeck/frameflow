"""Models used by file providers."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class FileCandidate:
    """Represents a candidate photo discovered by a provider."""

    library_id: str
    path: Path
    filename: str
    size: int
    modified_at: datetime
