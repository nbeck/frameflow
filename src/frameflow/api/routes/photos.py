"""Photo endpoints."""

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("/next")
def next_photo() -> dict[str, str]:
    """Placeholder endpoint until repositories are wired."""

    raise HTTPException(
        status_code=501,
        detail="Photo selection service not yet wired.",
    )
