"""Photo selection service."""

from collections.abc import Sequence

from frameflow.domain import DisplayEvent, Photo
from frameflow.rotation import RotationEngine


class PhotoSelectionService:
    """Coordinates photo selection."""

    def __init__(
        self,
        rotation_engine: RotationEngine | None = None,
    ) -> None:
        self._rotation_engine = rotation_engine or RotationEngine()

    def next_photo(
        self,
        photos: Sequence[Photo],
        history: Sequence[DisplayEvent],
    ) -> Photo | None:
        """Return the next photo."""

        return self._rotation_engine.next_photo(
            photos=photos,
            history=history,
        )
