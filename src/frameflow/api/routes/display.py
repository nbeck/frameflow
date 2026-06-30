"""Display client endpoints."""

import mimetypes
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import Path as FastAPIPath
from fastapi.responses import FileResponse

from frameflow.api.dependencies import get_photo_service
from frameflow.infrastructure.logging import get_logger
from frameflow.services import PhotoService

_logger = get_logger("frameflow.api.display")

router = APIRouter(prefix="/displays", tags=["displays"])


@router.get(
    "/{display_id}/photo",
    response_class=FileResponse,
    responses={
        200: {
            "content": {"image/*": {}},
            "description": "Photo file in its original format.",
        },
    },
)
def display_photo(
    display_id: Annotated[str, FastAPIPath(pattern=r"^[a-zA-Z0-9_-]{1,64}$")],
    request: Request,
    photo_service: Annotated[PhotoService, Depends(get_photo_service)],
) -> FileResponse:
    """Return the next photo in rotation for a display client."""

    try:
        photo = photo_service.get_next_photo(display_id)
    except Exception as exc:
        _logger.error("Rotation failed: display_id=%s", display_id, exc_info=True)
        raise HTTPException(status_code=500, detail="Photo rotation failed.") from exc

    if photo is None:
        _logger.warning("No photos available: display_id=%s", display_id)
        raise HTTPException(
            status_code=503,
            detail="No photos available.",
            headers={"Retry-After": "300"},
        )

    path = Path(photo.source_path).resolve()
    if not path.exists() or not path.is_file():
        _logger.warning(
            "Photo file missing: display_id=%s photo_id=%s path=%s",
            display_id,
            photo.id,
            path,
        )
        raise HTTPException(status_code=404, detail="Photo file not found.")

    client_ip = request.client.host if request.client else "unknown"
    _logger.info(
        "Photo served: display_id=%s photo_id=%s client_ip=%s",
        display_id,
        photo.id,
        client_ip,
    )

    media_type, _ = mimetypes.guess_type(path.name)

    return FileResponse(
        path=path,
        media_type=media_type or "application/octet-stream",
        filename=path.name,
        headers={
            "Cache-Control": "no-store, max-age=0",
            "X-Photo-Id": photo.id,
        },
    )
