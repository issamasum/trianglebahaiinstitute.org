"""Service layer for Check-in at TBI CRUD operations."""

from datetime import datetime

from ...tables.user import User
from .exceptions import CheckInNotFoundException, EventNotFoundException
from .repository import CheckInRepository, EventRepository
from .tables import (
    CheckIn,
    DietaryPreference,
    Event,
    EventCreationType,
    EventStatus,
)


class EventService:
    """Orchestrates creation, listing, retrieval, and deletion of events."""

    def __init__(self, event_repo: EventRepository) -> None:
        """Initializes the service with its repository dependency.

        Args:
            event_repo: Repository used to load and persit events.
        """
        self._event_repo = event_repo

    def create_event(
            self,
            subject: User,
            *,
            event_name: str,
            start_date: datetime | None = None,
            end_date: datetime | None = None,
            publish: bool = False,
    ) -> Event:
        """Creates a new event per an coordinator's request.

        Args:
            subject: the Cordinator creating the event
            event_name: Display name for the event.
            start_date: Optional scheduled start time.
            end_time: Optional scheduled end time.
            publish: Whether the event is visible to visitors or not.
        
        Returns:
            The created event.
        """
        event = Event(
            event_name=event_name,
            start_date=start_date,
            end_date=end_date,
            status=EventStatus.ACTIVE,
            publish=publish,
            creation_type=EventCreationType.MANUAL,
            created_by=subject.id,
            updated_by=subject.id,
        )
        return self._event_repo.create(event)

    def list_events(self) -> list[Event]:
        """Returns all the stored events.

        Args:
            None
        
        Returns:
            A list of all events.
        """
        return self._event_repo.list_events()

    def list_publisehd_events(self) -> list[Event]:
        """Returns all published and active events.

        Args:
            None
        
        Returns:
            A list of published and active events.
        """
        return self._event_repo.lists_published_active_events()

    def get_event(self, event_id: int) -> Event:
        """Returns a single event.

        Args:
            event_id: the requested event id.
        
            Returns:
                The particular event.
        """
        event = self._event_repo.get_by_id(event_id)
        if event is None:
            raise EventNotFoundException("Event not found.")
        return event

    def update_event(
        self,
        subject: User,
        event_id: int,
        *,
        event_name: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        publish: bool | None = None,
        status: EventStatus | None = None,
    ) -> Event:
        """Updates whichever fields are provided on an existing event.
 
        Args:
            subject: The coordinator making the change.
            event_id: The event the coordinator wants to update.
            event_name: New name.
            start_date: New start time.
            end_date: New end time.
            publish: New publish state.
            status: New status.
 
        Returns:
            The updated event.
 
        Raises:
            EventNotFoundException: If no event exists with that id.
        """
        event = self.get_event(event_id)
        if event_name is not None:
            event.event_name = event_name
        if start_date is not None:
            event.start_date = start_date
        if end_date is not None:
            event.end_date = end_date
        if publish is not None:
            event.publish = publish
        if status is not None:
            event.status = status
        event.updated_by = subject.id
        return self._event_repo.update(event)

    def cancel_event(self, subject: User, event_id: int) -> Event:
        """Soft-deletes an event by setting its status to canceled.
 
        Args:
            subject: The coordinator canceling the event.
            event_id: The event a coordinator wants to cancel.
 
        Returns:
            The canceled event.
 
        Raises:
            EventNotFoundException: If no event exists with that id.
        """
        event = self.get_event(event_id)
        event.updated_by = subject.id
        return self._event_repo.cancel_event(event)



# ---- CheckIn Service ---------

class CheckInService:
    """Orchestrates creation, listing, retrieval, and deletion of checkins."""
    
    def __init__(self, check_in_repo: CheckInRepository, event_repo: EventRepository) -> None:
        """Initializes the service with its repository dependency.
    
        Args:
            check_in_repo: Repository used to load and persist checkins.
            event_repo: Repository used to load and persit events.
        """
        self._check_in_repo = check_in_repo
        self._event_repo = event_repo

    def create_check_in(
        self,
        event_id: int,
        *,
        visitor_name: str,
        age: int | None = None,
        meal: bool = False,
        dietary_preferences: list[DietaryPreference] | None = None,
        allergies: str | None = None,
        user_id=None,
        require_published: bool = True,
    ) -> CheckIn:
        """Records a visitor's check-in to an existing event.
 
        Args:
            event_id: The event being checked into.
            visitor_name: The visitor's display name.
            age: Optional visitor age.
            meal: Whether the visitor is staying for a meal.
            dietary_preferences: Any dietary preferences the visitor selected.
            allergies: Allergy notes.
            user_id: The visitor's user id, if they are logged in.
            require_published: If True (visitor-facing call), the event must
                be published and active. Coordinators pass False to check
                visitors into any event, published or not.
 
        Returns:
            The newly created check-in.
 
        Raises:
            EventNotFoundException: If the event doesn't exist or not published.
        """
        event = self._event_repo.get_by_id(event_id)
        if event is None:
            raise EventNotFoundException("Event not found.")
        if require_published and (not event.publish or event.status != EventStatus.ACTIVE):
            raise EventNotFoundException("Checkins are Closed.")
 
        check_in = CheckIn(
            visitor_name=visitor_name,
            age=age,
            meal=meal,
            dietary_preferences=dietary_preferences or [],
            allergies=allergies,
            event_id=event_id,
            user_id=user_id,
        )
        return self._check_in_repo.create(check_in)
 
    def create_general_check_in(
        self,
        *,
        visitor_name: str,
        purpose: str,
        user_id=None,
    ) -> CheckIn:
        """Records a check-in with no scheduled event.
 
        Args:
            visitor_name: The visitor's display name.
            purpose: Reason for the visit.
            user_id: The visitor's user id, if they are logged in.
 
        Returns:
            The newly created check-in.
        """
        check_in = CheckIn(
            visitor_name=visitor_name,
            purpose=purpose,
            event_id=None,
            user_id=user_id,
        )
        return self._check_in_repo.create(check_in)
 
    def get_check_in(self, check_in_id: int) -> CheckIn:
        """Loads a single check-in by its id.
 
        Args:
            check_in_id: The specifc check-in record being requested.
 
        Returns:
            The returned check-in.
 
        Raises:
            CheckInNotFoundException: If no check-in exists with that id.
        """
        check_in = self._check_in_repo.get_by_id(check_in_id)
        if check_in is None:
            raise CheckInNotFoundException("Check-in not found.")
        return check_in
 
    def list_check_ins_for_event(self, event_id: int) -> list[CheckIn]:
        """Lists all check-ins records for a given event.
 
        Args:
            event_id: The event whose check-ins are being requested.
 
        Returns:
            The list of check-ins for that event.
 
        Raises:
            EventNotFoundException: If the event doesn't exist.
        """
        if self._event_repo.get_by_id(event_id) is None:
            raise EventNotFoundException("Event not found.")
        return self._check_in_repo.list_check_ins_by_event(event_id)
 
    def update_check_in(
        self,
        check_in_id: int,
        *,
        visitor_name: str | None = None,
        age: int | None = None,
        meal: bool | None = None,
        dietary_preferences: list[DietaryPreference] | None = None,
        allergies: str | None = None,
    ) -> CheckIn:
        """Updates whichever fields are provided on an existing check-in.
 
        Args:
            check_in_id: The check-in record needs a change.
            visitor_name: Updated visitor name.
            age: Updated age.
            meal: Updated meal preference.
            dietary_preferences: Updated dietary preferences.
            allergies: Updated allergy notes.
 
        Returns:
            The updated check-in.
 
        Raises:
            CheckInNotFoundException: If no check-in exists with that id.
        """
        check_in = self.get_check_in(check_in_id)
 
        if visitor_name is not None:
            check_in.visitor_name = visitor_name
        if age is not None:
            check_in.age = age
        if meal is not None:
            check_in.meal = meal
        if dietary_preferences is not None:
            check_in.dietary_preferences = dietary_preferences
        if allergies is not None:
            check_in.allergies = allergies
 
        return self._check_in_repo.update(check_in)
 
    def delete_check_in(self, check_in_id: int) -> None:
        """Hard-deletes a check-in record.
 
        Args:
            check_in_id: The check-in's primary key.
 
        Raises:
            CheckInNotFoundException: If no check-in exists with that id.
        """
        check_in = self.get_check_in(check_in_id)
        self._check_in_repo.delete(check_in)

        