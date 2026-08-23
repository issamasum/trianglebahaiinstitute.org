# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Check-in management routes for the public API."""

from typing import Annotated

from fastapi import APIRouter, Body

# from trianglebahaiinstitute.mytbi.checkin_at_tbi.tables import (
#     Event, 
#   CheckIn,
#   EventCreationType,
#   EventStatus,
    
# )

from ..models import (
    CreateEventRequest,
    EventResponse,
    UpdateEventRequest,
    CreateCheckInRequest,
    UpdateCheckInRequest,
    CheckInResponse,
    CreateGeneralCheckInRequest,
     
)

# ------ Admin Routes -------

admin_router = APIRouter(prefix="/admin/check-in/events", tags=["Admin Tools"])

@admin_router.post(
    "",
    response_model=EventResponse,
    status_code=201,
    summary="Create an event",
    response_description="The newly created event.",
    responses={
        401: {"description": "Not authenticated."},
        403: {"description": "Insufficient permissions."},
    },
)
def admin_create_event(
    body: Annotated[CreateEventRequest, Body()]
    ) -> EventResponse:
    """Creates a new event.
    
    Args:
        TBD

    Returns:
        The newly created event.
    """
    ...



@admin_router.get(
    "/analysis",
    summary="Analyze all events",
    responses={
        401: {"description": "Not authonticated."},
        403: {"description": "Insufficient permissions."},
    },
)
def admin_analyze_all_events():
    """Analyze all events."
    
    Args:
        TBD

    Returns:
        TBD
    """
    ...


@admin_router.get(
    "/{event_id}/analysis",
    summary="Analyze an event",
    responses={
        401: {"description": "Not authonticated."},
        403: {"description": "Insufficient permissions."},
        404: {"description": "Event not found."},
    },
)
def admin_analyze_event():
    """Analyze a single event."
    
    Args:
        TBD

    Returns:
        TBD
    """
    ...


@admin_router.get(
    "",
    response_model=EventResponse,
    status_code=200,
    summary="Gets all events",
    response_description="A list of all events.",
    responses={
        401: {"description": "Not authenticated."},
        403: {"description": "Insufficient permissions."},
        404: {"description": "Events not found."}, 
    },
)
def admin_list_events() -> list[EventResponse]:
    """Get all events.
    
    Args:
        TBD

    Returns:
        A list of all events.
    """
    ...


@admin_router.get(
    "/{event_id}",
    response_model=EventResponse,
    status_code=200,
    summary="Gets an event",
    response_description="Details of the event.",
    responses={
        401: {"description": "Not authenticated."},
        403: {"description": "Insufficient permissions."},
        404: {"description": "Event not found."}
        },
)
def admin_get_event() -> EventResponse:
    """Get a single event's details.
    
    Args:
        TBD

    Returns:
        A list of all events.
    """
    ...


@admin_router.patch(
    "/{event_id}",
    response_model=EventResponse,
    status_code=201,
    summary="Update an event",
    response_description="The updated event.",
    responses={
        401: {"description": "Not authenticated."},
        403: {"description": "Insufficient permissions."},
        404: {"description": "Event not found."},
        },
)
def admin_update_event(
    body: Annotated[UpdateEventRequest, Body()]
    ) -> EventResponse:
    """Update an existing event.
    
    Args:
        TBD

    Returns:
        The newly updated event.
    """
    ...


@admin_router.delete(
    "/{event_id}",
    status_code=204,
    summary="Soft delete an event",
    responses={
        401: {"description": "Not authenticated."},
        403: {"description": "Insufficient permissions."},
        404: {"description": "Event not found."},
    },
)
def admin_admin_delete_event() -> None:
    """Soft delete an event. Sets status to "canceled"
    
    Args:
        TBD

    Returns:
        None.
    """
    ...


# ---- Admin Check-in related routes --------


@admin_router.post(
    "/{event_id}/check-ins",
    response_model=CheckInResponse,
    status_code=201,
    summary="Add or check in a visitor to an existing event.",
    response_description="The newly added check-in.",
    responses={
        401: {"description": "Not authonticated."},
        403: {"description": "Insufficient permissions."},
        404: {"description": "Event not found."},
    },
)
def admin_create_check_in(
    body: Annotated[CreateCheckInRequest, Body()]
    ) -> CheckInResponse:
    """Adds a new check-in to an existing event.
    
    Args:
        TBD

    Returns:
        The newly added check-in.
    """
    ...


@admin_router.get(
    "/{event_id}/check-ins",
    response_model=list[CheckInResponse],
    status_code=200,
    summary="Lists check-ins for an existing event.",
    response_description="A list of checked in visitors of an event.",
    responses={
        401: {"description": "Not authenticated."},
        403: {"description": "Insufficient permissions."},
        404: {"description": "Event not found."},
    },
)
def admin_list_check_ins() -> list[CheckInResponse]:
    """Gets a list of all checked in visitors for an event.
    
    Args:
        TBD

    Returns:
        The list of checked in visitors.
    """
    ...


@admin_router.get(
    "/{event_id}/check-ins/{check_in_id}",
    response_model=CheckInResponse,
    status_code=200,
    summary="Get particular checked in visitor.",
    response_description="A check-in's details.",
    responses={
        401: {"description": "Not authenticated."},
        403: {"description": "Insufficient permissions."},
        404: {"description": "Check-in not found."},
    },
)
def admin_get_check_in() -> CheckInResponse:
    """Gets a single check-in's details.
    
    Args:
        TBD

    Returns:
        The check-in's details.
    """
    ...


@admin_router.patch(
    "/{event_id}/check-ins/{check_in_id}",
    response_model=CheckInResponse,
    status_code=201,
    summary="Updates a check-in.",
    response_description="The updated check-in.",
    responses={
        401: {"description": "Not authonticated."},
        403: {"description": "Insufficient permissions."},
        404: {"description": "Check-in not found."},
    },
)
def admin_update_check_in(
    body: Annotated[UpdateCheckInRequest, Body()]
    ) -> CheckInResponse:
    """Updates a chek-in.
    
    Args:
        TBD

    Returns:
        The updated check-in.
    """
    ...


@admin_router.delete(
    "/{event_id}/check-ins/{visitor_id}",
    status_code=201,
    summary="Hard deletes a check-in.",
    responses={
        401: {"description": "Not authonticated."},
        403: {"description": "Insufficient permissions."},
        404: {"description": "Check-in not found."},
    },
)
def admin_delete_check_in() -> None:
    """Hard deletion of a check-in.
    
    Args:
        TBD

    Returns:
        None.
    """
    ...

# ---- Admin general check-in route -------

admin_general_router = APIRouter(prefix="/admin/check-in", tag=["Admin Routes"])

@admin_general_router.post(
    "/general/check-ins",
    response_model=CheckInResponse,
    status_code=201,
    summary="Record a general check-in on behalf of a visitor.",
    response_description="The newly created check-in.",
    responses={
        401: {"description": "Not authenticated."},
        403: {"description": "Insufficient permissions."},
    },
)
def _admincreate_general_check_in(
    body: Annotated[CreateGeneralCheckInRequest, Body()]
    ) -> CheckInResponse:
    """Coordinator manually records a check-in with no scheduled event.
    
    Args:
        TBD

    Returns:
        The newly created check-in.
    """
    ...


# ----- Non-admin routes --------


router = APIRouter(prefix="/check-in", tags=["Check In"])


@router.get(
    "/events",
    response_model=list[EventResponse],
    status_code=200,
    summary="Lists publisehed and active events.",
    response_description="The list of published and active events.",
    responses={
        404: {"description": "Events not Found"}
    }
)
def list_events(
    ) -> list[EventResponse]:
    """Lists published and active events for visitors to see.
    
    Args:
        TBD

    Returns:
        A list of published and active events.
    """
    ...


@router.get(
    "/events/{event_id}",
    response_model=EventResponse,
    status_code=200,
    summary="Get a published event's details.",
    response_description="The event's name and dates.",
    responses={404: {"description": "Event not found."}},
)
def get_event() -> EventResponse:
    """Gets a single published event's details for the check-in form header.
 
    Does not return participant/check-in data — visitor-facing only.
 
    Args:
        TBD

    Returns:
        The event's name and dates.
    """
    ...


@router.post(
    "/events/{event_id}/check-ins",
    response_model=CheckInResponse,
    status_code=201,
    summary="Record a visitor's check-in to an existing event.",
    response_description="The newly created check-in.",
    responses={
        404: {"description": "Event not found."}
    },
)
def create_check_in(
    body: Annotated[CreateCheckInRequest, Body()]
    ) -> CheckInResponse:
    """Check-in for an event.
    
    Args:
        TBD

    Returns:
        The newly created check-in.
    """
    ...


@router.post(
    "/general/check-ins",
    response_model=CheckInResponse,
    status_code=201,
    summary="Record a general check-in.",
    response_description="The newly created check-in.",
)
def create_general_check_in(
    body: Annotated[CreateGeneralCheckInRequest, Body()]
    ) -> CheckInResponse:
    """Records a check-in with no scheduled event.
    
    Args:
        TBD

    Returns:
        The newly created check-in.
    """
    ...
