"""Rotation policies."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from frameflow.domain import DisplayEvent, Photo


class LeastRecentlyDisplayedPolicy:
    """Select the least recently displayed photo."""

    def select(
        self,
        photos: Sequence[Photo],
        history: Sequence[DisplayEvent],
    ) -> Photo | None:
        """Return the next photo to display."""

        if not photos:
            return None

        last_displayed = {event.photo_id: event.displayed_at for event in history}

        return min(
            photos,
            key=lambda photo: (
                photo.id in last_displayed,
                last_displayed.get(photo.id, datetime.min),
                photo.id,
            ),
        )
