# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Persistence helpers for Check-in at TBI records."""

from sqlmodel import select

from ...repositories.base_repository import BaseRepository
from .tables import (
    CheckIn,
    Event,
    EventStatus,
)


class EventRepository(BaseRepository[Event, int]):
    """Provides CRUD operations for event records."""

    @property
    def model_type(self) -> type[Event]:
        """Returns the SQLModel class managed by this repository."""
        return Event

    def list_events(self) -> list[Event]:
        """Returns all created events.

        Args:
            None

            Returns:
                A list of all events.
        """
        return list(self._session.exec(select(Event)).all())

    def lists_published_active_events(self) -> list[Event]:
        """Returns events that are visible to the visitors.

        Args:
            None

        Returns:
            A list of active events.
        """
        stmt = select(Event).where(
            Event.publish == True,  # noqa: E712
            Event.status == EventStatus.ACTIVE,
        )
        return list(self._session.exec(stmt).all())

    def cancel_event(self, event: Event) -> Event:
        """Sets the event's status to `Canceled`.

        Args:
            event: The event that an admon wants to cancel.

        Returns:
            The updated canceled event.
        """

        event.status = EventStatus.CANCELED
        return self.update(event)


class CheckInRepository(BaseRepository[CheckIn, int]):
    """Provides CRUD operations for check-in records."""

    @property
    def model_type(self) -> type[CheckIn]:
        """Returns the SQLModel class managed by this repository."""
        return CheckIn

    def list_check_ins_by_event(self, event_id: int) -> list[CheckIn]:
        """Lists check ins based on an event.

        Args:
            event_id: The specific event being requested

        Returns:
            List of all checked in visitors for that event.
        """

        stmt = select(CheckIn).where(CheckIn.event_id == event_id)
        return list(self._session.exec(stmt).all())
