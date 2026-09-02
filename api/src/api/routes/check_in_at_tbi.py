# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Check-in management routes for the public API."""

from typing import Annotated

from fastapi import APIRouter, Body, HTTPException

from trianglebahaiinstitute.mytbi.checkin_at_tbi.exceptions import (
    CheckInNotFoundException,
    EventNotFoundException,
)

from ..di import (
    CoordinatorUserDI,
    EventServiceDI,
    CheckInServiceDI,
)

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
    subject: CoordinatorUserDI,
    body: Annotated[CreateEventRequest, Body()],
    event_svc: EventServiceDI,
) -> EventResponse:
    """Creates a new event.
    Args:
        subject: The coordinator creating the event.
        body: The event's details.
        event_svc: Service used to create the event.

    Returns:
        The newly created event.
    """
    event = event_svc.create_event(
        subject,
        event_name=body.event_name,
        start_date=body.start_date,
        end_date=body.end_date,
        publish=body.publish,
    )
    return EventResponse.model_validate(event)


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
    response_model=list[EventResponse],
    status_code=200,
    summary="Gets all events",
    response_description="A list of all events.",
    responses={
        401: {"description": "Not authenticated."},
        403: {"description": "Insufficient permissions."},
    },
)
def admin_list_events(event_svc: EventServiceDI) -> list[EventResponse]:
    """Get all events.

    Args:
        subject: The coordinator requesting the list.
        event_svc: Service used to load events.

    Returns:
        A list of all events.
    """
    events = event_svc.list_events()
    return [EventResponse.model_validate(event) for event in events]


@admin_router.get(
    "/{event_id}",
    response_model=EventResponse,
    status_code=200,
    summary="Gets an event",
    response_description="Details of the event.",
    responses={
        401: {"description": "Not authenticated."},
        403: {"description": "Insufficient permissions."},
        404: {"description": "Event not found."},
    },
)
def admin_get_event(
    event_id: int,
    event_svc: EventServiceDI,
) -> EventResponse:
    """Get a single event's details.

    Args:
        event_id: The event being requested.
        event_svc: Serivce used to load the event.

    Returns:
        A list of all events.
    """
    try:
        event = event_svc.get_event(event_id)
    except EventNotFoundException:
        raise HTTPException(status_code=404, detail="Event not found.")
    return EventResponse.model_validate(event)


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
    subject: CoordinatorUserDI,
    event_id: int,
    body: Annotated[UpdateEventRequest, Body()],
    event_svc: EventServiceDI,
) -> EventResponse:
    """Update an existing event.

    Args:
        subject: The coordinator making the change.
        event_id: The event to update.
        body: The fields to update; fields left unset are untouched.
        event_svc: Service used to persist the change.

    Returns:
        The updated event.
    """
    try:
        event = event_svc.update_event(
            subject, event_id, **body.model_dump(exclude_unset=True)
        )
    except EventNotFoundException:
        raise HTTPException(status_code=404, detail="Event not found.")
    return EventResponse.model_validate(event)


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
def admin_admin_delete_event(
    subject: CoordinatorUserDI,
    event_id: int,
    event_svc: EventServiceDI,
) -> None:
    """Soft delete an event. Sets status to "canceled"

    Args:
        subject: the coordinator canceling the event.
        event_id: the event being cancelled.
        event_svc: Service to persist the change.

    Returns:
        None.
    """
    try:
        event_svc.cancel_event(subject, event_id)
    except EventNotFoundException:
        raise HTTPException(status_code=404, detail="Event not found.")


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
    event_id: int,
    body: Annotated[CreateCheckInRequest, Body()],
    check_in_svc: CheckInServiceDI,
) -> CheckInResponse:
    """Adds a new check-in to an existing event.

    Args:
         event_id: The event being checked into.
         body: The visitor's check-in details.
         check_in_svc: Service used to record the check-in.

     Returns:
         The newly added check-in.
    """
    try:
        check_in = check_in_svc.create_check_in(
            event_id,
            visitor_name=body.visitor_name,
            age=body.age,
            meal=body.meal,
            dietary_preferences=body.dietary_preferences,
            allergies=body.allergies,
            require_published=False,
        )
    except EventNotFoundException:
        raise HTTPException(status_code=404, detail="Event not found.")
    return CheckInResponse.model_validate(check_in)


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
def admin_list_check_ins(
    event_id: int,
    check_in_svc: CheckInServiceDI,
) -> list[CheckInResponse]:
    """Gets a list of all checked in visitors for an event.

    Args:
        event_id: The event the check-ins are registered for.
        check_in_svc: Service used to load check-ins.

    Returns:
        The list of checked in visitors.
    """
    try:
        check_ins = check_in_svc.list_check_ins_for_event(event_id)
    except EventNotFoundException:
        raise HTTPException(status_code=404, detail="Event not found.")
    return [CheckInResponse.model_validate(check_in) for check_in in check_ins]


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
def admin_get_check_in(
    event_id: int,
    check_in_id: int,
    check_in_svc: CheckInServiceDI,
) -> CheckInResponse:
    """Gets a single check-in's details.

    Args:
         event_id: The event the check-in belongs to.
         check_in_id: The check-in being requested.
         check_in_svc: Service used to load the check-in.

     Returns:
         The check-in's details.
    """
    try:
        check_in = check_in_svc.get_check_in_for_event(event_id, check_in_id)
    except CheckInNotFoundException:
        raise HTTPException(status_code=404, detail="Check-in not found.")
    return CheckInResponse.model_validate(check_in)


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
    event_id: int,
    check_in_id: int,
    body: Annotated[UpdateCheckInRequest, Body()],
    check_in_svc: CheckInServiceDI,
) -> CheckInResponse:
    """Updates a chek-in.

    Args:
         event_id: The event the check-in belong to.
         check_in_id: The check-in to update.
         body: The fields to update.
         check_in_svc: Service used to persist the change.

     Returns:
         The updated check-in.
    """
    try:
        check_in_svc.get_check_in_for_event(event_id, check_in_id)
    except CheckInNotFoundException:
        raise HTTPException(status_code=404, detail="Check-in not found.")
    updated = check_in_svc.update_check_in(
        check_in_id, **body.model_dump(exclude_unset=True)
    )
    return CheckInResponse.model_validate(updated)


@admin_router.delete(
    "/{event_id}/check-ins/{check_in_id}",
    status_code=201,
    summary="Hard deletes a check-in.",
    responses={
        401: {"description": "Not authonticated."},
        403: {"description": "Insufficient permissions."},
        404: {"description": "Check-in not found."},
    },
)
def admin_delete_check_in(
    event_id: int,
    check_in_id: int,
    check_in_svc: CheckInServiceDI,
) -> None:
    """Hard deletion of a check-in.

    Args:
        event_id: The event the check-in should belong to.
        check_in_id: The check-in to delete.
        check_in_svc: Service used to persist the deletion.

    Returns:
        None.
    """
    try:
        check_in_svc.get_check_in_for_event(event_id, check_in_id)
    except CheckInNotFoundException:
        raise HTTPException(status_code=404, detail="Check-in not found.")
    check_in_svc.delete_check_in(check_in_id)


# ---- Admin general check-in route -------


admin_general_router = APIRouter(prefix="/admin/check-in", tags=["Admin Tools"])


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
def admin_create_general_check_in(
    body: Annotated[CreateGeneralCheckInRequest, Body()],
    check_in_svc: CheckInServiceDI,
) -> CheckInResponse:
    """Coordinator manually records a check-in with no scheduled event.

    Args:
        body: The visitor's name and reason for visiting.
        check_in_svc: Service used to record the check-in.

    Returns:
        The newly created check-in.
    """
    check_in = check_in_svc.create_general_check_in(
        visitor_name=body.visitor_name, purpose=body.purpose
    )
    return CheckInResponse.model_validate(check_in)


# ----- Non-admin routes --------


router = APIRouter(prefix="/check-in", tags=["Check In"])


@router.get(
    "/events",
    response_model=list[EventResponse],
    status_code=200,
    summary="Lists publisehed and active events.",
    response_description="The list of published and active events.",
)
def list_events(event_svc: EventServiceDI) -> list[EventResponse]:
    """Lists published and active events for visitors to see.

    Args:
        event_svc: Service used to load events.

    Returns:
        A list of published and active events.
    """
    events = event_svc.list_published_events()
    return [EventResponse.model_validate(event) for event in events]


@router.get(
    "/events/{event_id}",
    response_model=EventResponse,
    status_code=200,
    summary="Get a published event's details.",
    response_description="The event's name and dates.",
    responses={404: {"description": "Event not found."}},
)
def get_event(event_id: int, event_svc: EventServiceDI) -> EventResponse:
    """Gets a single published event's details for the check-in form header.

    Does not return participant/check-in data.

    Args:
        event_id: The event being requested.
        event_svc: Service used to load the event.

    Returns:
        The event's name and dates.
    """
    try:
        event = event_svc.get_published_event(event_id)
    except EventNotFoundException:
        raise HTTPException(status_code=404, detail="Event not found.")
    return EventResponse.model_validate(event)


@router.post(
    "/events/{event_id}/check-ins",
    response_model=CheckInResponse,
    status_code=201,
    summary="Record a visitor's check-in to an existing event.",
    response_description="The newly created check-in.",
    responses={404: {"description": "Event not found."}},
)
def create_check_in(
    event_id: int,
    body: Annotated[CreateCheckInRequest, Body()],
    check_in_svc: CheckInServiceDI,
) -> CheckInResponse:
    """Check-in for an event.

     Args:
        event_id: The event being checked into.
        body: The visitor's check-in details.
        check_in_svc: Service used to record the check-in.

    Returns:
        The newly created check-in.
    """
    try:
        check_in = check_in_svc.create_check_in(
            event_id,
            visitor_name=body.visitor_name,
            age=body.age,
            meal=body.meal,
            dietary_preferences=body.dietary_preferences,
            allergies=body.allergies,
        )
    except EventNotFoundException:
        raise HTTPException(status_code=404, detail="Event not found.")
    return CheckInResponse.model_validate(check_in)


@router.post(
    "/general/check-ins",
    response_model=CheckInResponse,
    status_code=201,
    summary="Record a general check-in.",
    response_description="The newly created check-in.",
)
def create_general_check_in(
    body: Annotated[CreateGeneralCheckInRequest, Body()],
    check_in_svc: CheckInServiceDI,
) -> CheckInResponse:
    """Records a check-in with no scheduled event.

    Args:
        body: The visitor's name and reason for visiting.
        check_in_svc: Service used to record the check-in.

    Returns:
        The newly created check-in.
    """
    check_in = check_in_svc.create_general_check_in(
        visitor_name=body.visitor_name, purpose=body.purpose
    )
    return CheckInResponse.model_validate(check_in)
