"""Rotation engine."""

from __future__ import annotations

from collections.abc import Sequence

from frameflow.domain import DisplayEvent, Photo

from .policies import LeastRecentlyDisplayedPolicy


class RotationEngine:
    """Select the next photo for display."""

    def __init__(
        self,
        policy: LeastRecentlyDisplayedPolicy | None = None,
    ) -> None:
        self._policy = policy or LeastRecentlyDisplayedPolicy()

    def next_photo(
        self,
        photos: Sequence[Photo],
        history: Sequence[DisplayEvent],
    ) -> Photo | None:
        """Return the next photo."""

        return self._policy.select(photos, history)
