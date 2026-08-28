# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Pydantic models for checkin at TBI API requests and responses."""

from datetime import datetime
from typing import Optional
import uuid


from trianglebahaiinstitute.mytbi.checkin_at_tbi.tables import EventStatus, EventCreationType, DietaryPreference

from pydantic import BaseModel


# -----Events----------


class CreateEventRequest(BaseModel):
    """Payload for updating an event."""

    event_name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    publish: bool = False


class UpdateEventRequest(BaseModel):
    """Payload for creating an event."""

    event_name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    publish: Optional[bool] = None
    status: Optional[EventStatus] = None


class EventResponse(BaseModel):
    """Response for a created event."""

    model_config = {"from_attributes": True}

    id: int
    event_name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: EventStatus
    publish: bool 
    creation_type: EventCreationType
    external_calender_id: Optional[str] = None
    created_by: uuid.UUID
    created_at: datetime
    updated_by: uuid.UUID
    updated_at: datetime


# -----Checkins---------


class CreateGeneralCheckInRequest(BaseModel):
    """Payload for a general check in not associated with an event."""

    visitor_name: str
    purpose: str


class CreateCheckInRequest(BaseModel):
    """Payload for checking in at the TBI."""

    visitor_name: str
    age: Optional[int] = None
    meal: bool = False
    dietary_preferences: list[DietaryPreference] = []
    allergies: Optional[str] = None


class UpdateCheckInRequest(BaseModel):
    """Payload for checking in at the TBI."""

    visitor_name: Optional[str] = None
    age: Optional[int] = None
    meal: Optional[bool] = None
    dietary_preferences: Optional[list[DietaryPreference]] = None
    allergies: Optional[str] = None


class CheckInResponse(BaseModel):
    """Payload for checking in at the TBI."""

    id: int
    visitor_name: str
    age: Optional[int] = None
    meal: Optional[bool] = None
    dietary_preferences: list[DietaryPreference] = []
    allergies: Optional[str] = None
    event_id: Optional[int] = None
    user_id: Optional[uuid.UUID] = None
    purpose: Optional[str] = None
    checked_in_at: datetime
