"""Provider abstractions."""

from .models import FileCandidate
from .protocols import FileProvider

__all__ = [
    "FileCandidate",
    "FileProvider",
]
