"""Operational health routes for the API."""

from fastapi import APIRouter
from trianglebahaiinstitute.services.health import get_health_status


router = APIRouter(tags=["Operations"])


@router.get(
    "/health",
    summary="Get service health",
    response_description="Current health details for the API service.",
)
def health() -> dict[str, str]:
    """Returns the current service health payload."""
    return get_health_status()
