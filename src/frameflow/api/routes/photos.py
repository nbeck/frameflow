"""Photo endpoints."""

import io
import mimetypes
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, Response
from PIL import Image

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


@router.get("/{photo_id}/thumbnail")
def photo_thumbnail(
    photo_id: str,
    photo_service: Annotated[PhotoService, Depends(get_photo_service)],
) -> Response:
    """Return a thumbnail for the given photo."""

    photo = photo_service.get_photo_by_id(photo_id)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found.")

    path = Path(photo.source_path).resolve()
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="Photo file not found.")

    try:
        with Image.open(path) as source:
            rgb = source.convert("RGB")
            rgb.thumbnail((400, 400))
            buffer = io.BytesIO()
            rgb.save(buffer, format="JPEG")
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Thumbnail could not be generated.") from exc

    return Response(
        content=buffer.getvalue(),
        media_type="image/jpeg",
    )


@router.get("/next")
def next_photo(
    client_id: str,
    photo_service: Annotated[PhotoService, Depends(get_photo_service)],
) -> FileResponse:
    """Return the next photo for display."""

    if not client_id.strip():
        raise HTTPException(status_code=422, detail="client_id must not be blank.")

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
