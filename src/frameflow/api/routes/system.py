"""System endpoints."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends

from frameflow.api.dependencies import get_photo_service, get_settings
from frameflow.config import Settings
from frameflow.providers.local import SUPPORTED_IMAGE_EXTENSIONS
from frameflow.services import PhotoService

router = APIRouter(tags=["system"])


@router.get("/status")
def status(
    photo_service: Annotated[PhotoService, Depends(get_photo_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, object]:
    """Return API status and runtime health indicators."""

    library_path = settings.photo_library
    library_exists = Path(library_path).is_dir()
    photo_count = len(photo_service.list_photos())

    return {
        "status": "ok",
        "library_path": library_path,
        "library_exists": library_exists,
        "photo_count": photo_count,
    }


@router.get("/config")
def config(
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, object]:
    """Return safe runtime configuration."""

    return {
        "library_path": settings.photo_library,
        "environment": settings.environment,
        "log_level": settings.log_level,
        "supported_extensions": sorted(SUPPORTED_IMAGE_EXTENSIONS),
    }
