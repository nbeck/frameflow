from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Health endpoint for Docker and monitoring."""

    return {"status": "ok"}
