"""Photo endpoints."""

import io
import mimetypes
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, Response
from PIL import Image

from frameflow.api.dependencies import get_photo_service
from frameflow.api.schemas import PhotoSummary
from frameflow.infrastructure.logging import get_logger
from frameflow.services import PhotoService

_logger = get_logger("frameflow.api")

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("", response_model=list[PhotoSummary])
def list_photos(
    photo_service: Annotated[PhotoService, Depends(get_photo_service)],
) -> list[PhotoSummary]:
    """Return metadata for all known photos."""

    return [
        PhotoSummary(id=photo.id, source_path=str(photo.source_path))
        for photo in photo_service.list_photos()
    ]


@router.get(
    "/{photo_id}/thumbnail",
    response_class=Response,
    responses={
        200: {
            "content": {"image/jpeg": {}},
            "description": "JPEG thumbnail, max 400x400 pixels.",
        },
    },
)
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
        _logger.warning(
            "Thumbnail generation failed: photo_id=%s path=%s", photo_id, path, exc_info=True
        )
        raise HTTPException(status_code=500, detail="Thumbnail could not be generated.") from exc

    return Response(
        content=buffer.getvalue(),
        media_type="image/jpeg",
    )


@router.get(
    "/next",
    response_class=FileResponse,
    responses={
        200: {
            "content": {"image/*": {}},
            "description": "Photo file in its original format.",
        },
    },
)
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
