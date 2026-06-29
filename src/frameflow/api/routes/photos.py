"""Photo endpoints."""

import mimetypes
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from frameflow.api.dependencies import get_photo_service
from frameflow.services import PhotoService

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("")
def list_photos(
    photo_service: Annotated[PhotoService, Depends(get_photo_service)],
) -> list[dict[str, str | None]]:
    """Return metadata for all known photos."""

    return [
        {
            "id": photo.id,
            "source_path": str(photo.source_path),
            "content_hash": photo.content_hash,
        }
        for photo in photo_service.list_photos()
    ]


@router.get("/next")
def next_photo(
    client_id: str,
    photo_service: Annotated[PhotoService, Depends(get_photo_service)],
) -> FileResponse:
    """Return the next photo for display."""

    photo = photo_service.get_next_photo(client_id)
    if photo is None:
        raise HTTPException(status_code=404, detail="No photos available.")

    path = Path(photo.source_path).resolve()

    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="Photo file not found.")

    media_type, _ = mimetypes.guess_type(path.name)

    return FileResponse(
        path=path,
        media_type=media_type or "application/octet-stream",
        filename=path.name,
    )
