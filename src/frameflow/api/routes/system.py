"""System endpoints."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from frameflow.api.dependencies import (
    get_photo_service,
    get_scan_scheduler,
    get_settings,
    get_sync_state,
)
from frameflow.api.schemas import ConfigResponse, StatusResponse, SyncResponse
from frameflow.config import Settings
from frameflow.infrastructure.logging import get_logger
from frameflow.providers.local import SUPPORTED_IMAGE_EXTENSIONS
from frameflow.scanning import ScanScheduler, SyncAlreadyRunningError, SyncState
from frameflow.services import PhotoService

_logger = get_logger("frameflow.api")

router = APIRouter(tags=["system"])


@router.get("/status", response_model=StatusResponse)
def status(
    photo_service: Annotated[PhotoService, Depends(get_photo_service)],
    settings: Annotated[Settings, Depends(get_settings)],
    sync_state: Annotated[SyncState, Depends(get_sync_state)],
) -> StatusResponse:
    """Return API status and runtime health indicators."""

    library_path = settings.photo_library
    library_exists = Path(library_path).is_dir()
    photo_count = len(photo_service.list_photos())

    return StatusResponse(
        status="ok",
        library_path=library_path,
        library_exists=library_exists,
        photo_count=photo_count,
        last_sync_completed_at=(
            sync_state.last_sync_completed_at.isoformat()
            if sync_state.last_sync_completed_at
            else None
        ),
        last_sync_photos_processed=sync_state.last_sync_photos_processed,
        sync_running=sync_state.sync_running,
    )


@router.post("/sync", response_model=SyncResponse)
def trigger_sync(
    scheduler: Annotated[ScanScheduler, Depends(get_scan_scheduler)],
    sync_state: Annotated[SyncState, Depends(get_sync_state)],
) -> SyncResponse:
    """Trigger a single photo library synchronization run."""

    _logger.info("Manual sync requested")
    try:
        count = scheduler.run_once()
    except SyncAlreadyRunningError as exc:
        _logger.debug("Manual sync rejected: sync already in progress")
        raise HTTPException(status_code=409, detail="Sync already in progress.") from exc
    except Exception as exc:
        _logger.error("Manual sync failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Sync failed unexpectedly.") from exc
    _logger.info("Manual sync completed: %d photos processed", count)

    if sync_state.last_sync_completed_at is None:
        _logger.error("Sync completed but sync state was not updated")
        raise HTTPException(
            status_code=500,
            detail="Sync completed but state could not be read.",
        )
    return SyncResponse(
        status="ok",
        photos_processed=count,
        sync_completed_at=sync_state.last_sync_completed_at.isoformat(),
    )


@router.get("/config", response_model=ConfigResponse)
def config(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ConfigResponse:
    """Return safe runtime configuration."""

    return ConfigResponse(
        library_path=settings.photo_library,
        environment=settings.environment,
        log_level=settings.log_level,
        supported_extensions=sorted(SUPPORTED_IMAGE_EXTENSIONS),
    )
