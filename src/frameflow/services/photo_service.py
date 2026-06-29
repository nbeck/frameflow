"""Photo orchestration service."""

from datetime import UTC, datetime

from frameflow.domain import DisplayEvent, Photo
from frameflow.history import RotationHistoryRepository
from frameflow.services.photo_selection import PhotoSelectionService
from frameflow.storage import PhotoRepository


class PhotoService:
    """Application service for photo display workflows."""

    def __init__(
        self,
        photo_repository: PhotoRepository,
        history_repository: RotationHistoryRepository,
        selection_service: PhotoSelectionService,
    ) -> None:
        self._photo_repository = photo_repository
        self._history_repository = history_repository
        self._selection_service = selection_service

    def get_photo_by_id(self, photo_id: str) -> Photo | None:
        """Return a photo by its canonical ID."""
        return self._photo_repository.get_by_id(photo_id)

    def list_photos(self) -> list[Photo]:
        """Return all known photos."""
        return self._photo_repository.list_all()

    def get_next_photo(self, client_id: str) -> Photo | None:
        """Return and record the next photo for a client.

        Returns None if no photos are available or the selected photo's
        source file no longer exists on disk.
        """

        photos = self._photo_repository.list_all()
        history = self._history_repository.recent_for_client(client_id)

        selected_photo = self._selection_service.next_photo(photos, history)
        if selected_photo is None:
            return None

        if not selected_photo.source_path.exists():
            self._photo_repository.mark_unavailable({selected_photo.source_path})
            return None

        self._history_repository.record(
            DisplayEvent(
                photo_id=selected_photo.id,
                client_id=client_id,
                displayed_at=datetime.now(UTC),
            )
        )

        return selected_photo
