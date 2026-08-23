# Copyright (c) 2026 Issa Masumbuko
# SPDX-LIcence-Identifier: MIT

"""Database-backed checkin at TBI models"""

import enum
from datetime import datetime

from sqlalchemy import ARRAY, Column, DateTime, ForeignKey, Integer, String, func
from sqlmodel import Enum, Field, SQLModel


class EventStatus(str, enum.Enum):
    """Defines an event's status."""

    ACTIVE = "active"
    ENDED = "ended"
    CANCELED = "canceled"


class EventCreationType(str, enum.Enum):
    """ Defines how an event was created."""

    MANUAL = "manual"
    SYNCED = "synced"
    SYSTEM = "system"

class DietaryPreference(str, enum.Enum):
    """Defines various options for dietary preferences."""

    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    HALAL = "halal"
    KOSHER = "kosher"
    OTHER = "other"



class Event(SQLModel, table=True):
    """Represents an event being held at the triangle Baha'i Institute."""

    id: int = Field(
        sa_column=Column(Integer, primary_key=True, autoincrement=True)
    )
    event_name: str = Field(
        nullable=False
    )
    start_date: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
        ),
        default=None
    )
    end_date: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
        ),
        default=None
    )
    status: EventStatus = Field(
        sa_column=Column(
            Enum(
                EventStatus,
                values_callable=lambda e: [m.value for m in e]),
                nullable=False,
            ),
            default=EventStatus.ACTIVE.value
       
    )
    publish: bool = Field(
        default=True
    )
    creation_type: EventCreationType =  Field(
        sa_column=Column(
            Enum(
             EventCreationType,
                values_callable=lambda e: [m.value for m in e]),
                nullable=False,
            ),
            default=EventCreationType.MANUAL.value
    )
    external_calender_id: str = Field(
        sa_column=Column(String, nullable=True),
        default=None,
    
    )
    created_by: int = Field(
        sa_column=Column(Integer, ForeignKey("user.id"), nullable=False)
    )
    updated_by: int = Field(
            sa_column=Column(Integer, ForeignKey("user.id"), nullable=False)
        )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        default=None,
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
        default=None,
    )


class CheckIn(SQLModel, table=True):
    """Represents a checked in visitor at the Triangle Baha'i Institute."""

    id: int = Field(
            sa_column=Column(Integer, primary_key=True, autoincrement=True)
        )
    visitor_name: str = Field(
            nullable=False
    )
    age: int = Field(nullable=True)
    meal: bool = Field(default=False)
    dietary_preferences: list[DietaryPreference] = Field(
        sa_column=Column(
            ARRAY(
                Enum(DietaryPreference, values_callable=lambda e: [m.value for m in e])
                ), 
                nullable=True),
        default_factory=list,
    )
    allergies: str = Field(nullable=True)
    purpose: str = Field(nullable=True)
    event_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("event.id"), nullable=True
            )
    )
    user_id: int = Field(
            sa_column=Column(
                Integer, ForeignKey("user.id"), nullable=True
                )
        )
    checked_in_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        default=None,
    )
   