from fastapi import APIRouter

from frameflow.api.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Health endpoint for Docker and monitoring."""

    return HealthResponse(status="ok")
