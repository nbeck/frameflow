"""Provider interfaces."""

from collections.abc import Iterable
from typing import Protocol

from .models import FileCandidate


class FileProvider(Protocol):
    """Interface implemented by all photo providers."""

    def discover(self) -> Iterable[FileCandidate]:
        """Return discovered photo candidates."""
