"""OpenAPI metadata and customization for TriangleBahaiInstitute.org."""

from fastapi.routing import APIRoute


def generate_openation_id(route: APIRoute) -> str:
    """Uses the Python functon name as the OpenAPI operationId."""
    return route.name


API_DESCRIPTION = (
    "HTTP for TriangleBahaiInstitute.org, including operational endpoins, "
    "authentication flows, and feature management."
)

OPENAPI_TAGS: list[dict[str, str]] = [
    {
        "name": "Operations",
        "description": "Health check and openrational endpoints for the service.",
    },
    {"name": "Authentication", "description": "Sign-up, login, and token issuance."},
    {
        "name": "Authenticated User",
        "description": "Authenticated user profile access and updates.",
    },
    {"name": "Admin Tools", "description": "Coordinator-only management."},
    {
        "name": "Check In",
        "description": "Visitor-facing event listings and check-in submission.",
    },
]
