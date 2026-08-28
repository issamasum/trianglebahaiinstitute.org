"""Tests for EventService and CheckInService."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock
from uuid import uuid4

import pytest

from trianglebahaiinstitute.mytbi.checkin_at_tbi.exceptions import (
    CheckInNotFoundException,
    EventNotFoundException,
)
from trianglebahaiinstitute.mytbi.checkin_at_tbi.repository import (
    CheckInRepository,
    EventRepository,
)
from trianglebahaiinstitute.mytbi.checkin_at_tbi.service import (
    CheckInService,
    EventService,
)
from trianglebahaiinstitute.mytbi.checkin_at_tbi.tables import (
    CheckIn,
    DietaryPreference,
    Event,
    EventCreationType,
    EventStatus,
)
from trianglebahaiinstitute.tables.user import User

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_event_repo() -> Mock:
    """Create a mock EventRepository."""
    return MagicMock(spec=EventRepository)


@pytest.fixture
def mock_check_in_repo() -> Mock:
    """Create a mock CheckInRepository."""
    return MagicMock(spec=CheckInRepository)


@pytest.fixture
def event_service(mock_event_repo: Mock) -> EventService:
    """Create an EventService with mocked repository."""
    return EventService(mock_event_repo)


@pytest.fixture
def check_in_service(mock_check_in_repo: Mock, mock_event_repo: Mock) -> CheckInService:
    """Create a CheckInService with mocked repositories."""
    return CheckInService(mock_check_in_repo, mock_event_repo)


@pytest.fixture
def sample_user() -> User:
    """Create a sample user for testing."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    return user


@pytest.fixture
def sample_event() -> Event:
    """Create a sample event for testing."""
    return Event(
        id=1,
        event_name="Test Event",
        start_date=datetime(2026, 9, 1, 10, 0, 0, tzinfo=timezone.utc),
        end_date=datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc),
        status=EventStatus.ACTIVE,
        publish=True,
        creation_type=EventCreationType.MANUAL,
        created_by=uuid4(),
        updated_by=uuid4(),
    )


@pytest.fixture
def sample_published_event() -> Event:
    """Create a sample published and active event."""
    return Event(
        id=2,
        event_name="Published Event",
        status=EventStatus.ACTIVE,
        publish=True,
        creation_type=EventCreationType.MANUAL,
        created_by=uuid4(),
        updated_by=uuid4(),
    )


@pytest.fixture
def sample_unpublished_event() -> Event:
    """Create a sample unpublished event."""
    return Event(
        id=3,
        event_name="Unpublished Event",
        status=EventStatus.ACTIVE,
        publish=False,
        creation_type=EventCreationType.MANUAL,
        created_by=uuid4(),
        updated_by=uuid4(),
    )


@pytest.fixture
def sample_canceled_event() -> Event:
    """Create a sample canceled event."""
    return Event(
        id=4,
        event_name="Canceled Event",
        status=EventStatus.CANCELED,
        publish=True,
        creation_type=EventCreationType.MANUAL,
        created_by=uuid4(),
        updated_by=uuid4(),
    )


@pytest.fixture
def sample_check_in() -> CheckIn:
    """Create a sample check-in for testing."""
    return CheckIn(
        id=1,
        visitor_name="John Doe",
        age=25,
        meal=True,
        dietary_preferences=[DietaryPreference.VEGETARIAN],
        allergies="peanuts",
        event_id=1,
        user_id=uuid4(),
    )


# ============================================================================
# EVENT SERVICE TESTS
# ============================================================================


def test_event_service_init_stores_repository(mock_event_repo: Mock) -> None:
    """Test that init stores the repository reference."""
    service = EventService(mock_event_repo)
    assert service._event_repo is mock_event_repo


def test_event_service_create_event_with_all_parameters(
    event_service: EventService, mock_event_repo: Mock, sample_user: User
) -> None:
    """Test creating an event with all parameters."""
    start = datetime(2026, 9, 15, 10, 0, 0, tzinfo=timezone.utc)
    end = datetime(2026, 9, 15, 12, 0, 0, tzinfo=timezone.utc)
    created_event = Event(
        id=1,
        event_name="Summer Event",
        start_date=start,
        end_date=end,
        status=EventStatus.ACTIVE,
        publish=True,
        creation_type=EventCreationType.MANUAL,
        created_by=sample_user.id,
        updated_by=sample_user.id,
    )
    mock_event_repo.create.return_value = created_event

    result = event_service.create_event(
        sample_user,
        event_name="Summer Event",
        start_date=start,
        end_date=end,
        publish=True,
    )

    assert result == created_event
    assert result.event_name == "Summer Event"
    assert result.start_date == start
    assert result.end_date == end
    assert result.publish is True
    assert result.status == EventStatus.ACTIVE
    assert result.creation_type == EventCreationType.MANUAL
    assert result.created_by == sample_user.id
    assert result.updated_by == sample_user.id
    mock_event_repo.create.assert_called_once()


def test_event_service_create_event_with_minimal_parameters(
    event_service: EventService, mock_event_repo: Mock, sample_user: User
) -> None:
    """Test creating an event with only required parameters."""
    created_event = Event(
        id=1,
        event_name="Simple Event",
        status=EventStatus.ACTIVE,
        publish=False,
        creation_type=EventCreationType.MANUAL,
        created_by=sample_user.id,
        updated_by=sample_user.id,
    )
    mock_event_repo.create.return_value = created_event

    result = event_service.create_event(
        sample_user,
        event_name="Simple Event",
    )

    assert result.event_name == "Simple Event"
    assert result.start_date is None
    assert result.end_date is None
    assert result.publish is False
    assert result.status == EventStatus.ACTIVE


def test_event_service_create_event_publishes_by_default_false(
    event_service: EventService, mock_event_repo: Mock, sample_user: User
) -> None:
    """Test that publish defaults to False."""
    created_event = Event(
        id=1,
        event_name="Event",
        status=EventStatus.ACTIVE,
        publish=False,
        creation_type=EventCreationType.MANUAL,
        created_by=sample_user.id,
        updated_by=sample_user.id,
    )
    mock_event_repo.create.return_value = created_event

    result = event_service.create_event(sample_user, event_name="Event")

    assert result.publish is False


def test_event_service_list_events_returns_all_events(
    event_service: EventService, mock_event_repo: Mock, sample_event: Event
) -> None:
    """Test listing all events."""
    events = [sample_event]
    mock_event_repo.list_events.return_value = events

    result = event_service.list_events()

    assert result == events
    assert len(result) == 1
    mock_event_repo.list_events.assert_called_once()


def test_event_service_list_events_returns_empty_list(
    event_service: EventService, mock_event_repo: Mock
) -> None:
    """Test listing events when none exist."""
    mock_event_repo.list_events.return_value = []

    result = event_service.list_events()

    assert result == []
    assert len(result) == 0


def test_event_service_list_published_events_returns_published_and_active(
    event_service: EventService, mock_event_repo: Mock, sample_published_event: Event
) -> None:
    """Test listing published and active events."""
    events = [sample_published_event]
    mock_event_repo.lists_published_active_events.return_value = events

    result = event_service.list_publisehd_events()

    assert result == events
    assert len(result) == 1
    mock_event_repo.lists_published_active_events.assert_called_once()


def test_event_service_list_published_events_returns_empty_list(
    event_service: EventService, mock_event_repo: Mock
) -> None:
    """Test listing published events when none exist."""
    mock_event_repo.lists_published_active_events.return_value = []

    result = event_service.list_publisehd_events()

    assert result == []


def test_event_service_get_event_returns_existing_event(
    event_service: EventService, mock_event_repo: Mock, sample_event: Event
) -> None:
    """Test retrieving an existing event."""
    mock_event_repo.get_by_id.return_value = sample_event

    result = event_service.get_event(1)

    assert result == sample_event
    mock_event_repo.get_by_id.assert_called_once_with(1)


def test_event_service_get_event_raises_exception_when_not_found(
    event_service: EventService, mock_event_repo: Mock
) -> None:
    """Test that EventNotFoundException is raised when event not found."""
    mock_event_repo.get_by_id.return_value = None

    with pytest.raises(EventNotFoundException, match="Event not found."):
        event_service.get_event(999)


def test_event_service_update_event_all_fields(
    event_service: EventService, mock_event_repo: Mock, sample_user: User, sample_event: Event
) -> None:
    """Test updating all fields of an event."""
    mock_event_repo.get_by_id.return_value = sample_event
    updated_event = Event(
        id=1,
        event_name="Updated Event",
        start_date=datetime(2026, 10, 1, 10, 0, 0, tzinfo=timezone.utc),
        end_date=datetime(2026, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
        status=EventStatus.ENDED,
        publish=False,
        creation_type=EventCreationType.MANUAL,
        created_by=sample_event.created_by,
        updated_by=sample_user.id,
    )
    mock_event_repo.update.return_value = updated_event

    new_start = datetime(2026, 10, 1, 10, 0, 0, tzinfo=timezone.utc)
    new_end = datetime(2026, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    result = event_service.update_event(
        sample_user,
        1,
        event_name="Updated Event",
        start_date=new_start,
        end_date=new_end,
        publish=False,
        status=EventStatus.ENDED,
    )

    assert result.event_name == "Updated Event"
    assert result.publish is False
    assert result.status == EventStatus.ENDED
    assert result.updated_by == sample_user.id


def test_event_service_update_event_single_field(
    event_service: EventService, mock_event_repo: Mock, sample_user: User, sample_event: Event
) -> None:
    """Test updating a single field."""
    mock_event_repo.get_by_id.return_value = sample_event
    updated_event = Event(
        id=1,
        event_name="New Name",
        start_date=sample_event.start_date,
        end_date=sample_event.end_date,
        status=sample_event.status,
        publish=sample_event.publish,
        creation_type=sample_event.creation_type,
        created_by=sample_event.created_by,
        updated_by=sample_user.id,
    )
    mock_event_repo.update.return_value = updated_event

    result = event_service.update_event(sample_user, 1, event_name="New Name")

    assert result.event_name == "New Name"
    mock_event_repo.update.assert_called_once()


def test_event_service_update_event_no_fields_provided(
    event_service: EventService, mock_event_repo: Mock, sample_user: User, sample_event: Event
) -> None:
    """Test updating an event with no field changes."""
    mock_event_repo.get_by_id.return_value = sample_event
    mock_event_repo.update.return_value = sample_event

    result = event_service.update_event(sample_user, 1)

    assert result == sample_event
    mock_event_repo.update.assert_called_once()


def test_event_service_update_event_not_found(
    event_service: EventService, mock_event_repo: Mock, sample_user: User
) -> None:
    """Test updating a non-existent event."""
    mock_event_repo.get_by_id.return_value = None

    with pytest.raises(EventNotFoundException, match="Event not found."):
        event_service.update_event(sample_user, 999, event_name="New Name")


def test_event_service_cancel_event_sets_status_to_canceled(
    event_service: EventService, mock_event_repo: Mock, sample_user: User, sample_event: Event
) -> None:
    """Test canceling an existing event."""
    mock_event_repo.get_by_id.return_value = sample_event
    canceled_event = Event(
        id=1,
        event_name=sample_event.event_name,
        start_date=sample_event.start_date,
        end_date=sample_event.end_date,
        status=EventStatus.CANCELED,
        publish=sample_event.publish,
        creation_type=sample_event.creation_type,
        created_by=sample_event.created_by,
        updated_by=sample_user.id,
    )
    mock_event_repo.cancel_event.return_value = canceled_event

    result = event_service.cancel_event(sample_user, 1)

    assert result.status == EventStatus.CANCELED
    assert result.updated_by == sample_user.id
    mock_event_repo.cancel_event.assert_called_once()


def test_event_service_cancel_event_not_found(
    event_service: EventService, mock_event_repo: Mock, sample_user: User
) -> None:
    """Test canceling a non-existent event."""
    mock_event_repo.get_by_id.return_value = None

    with pytest.raises(EventNotFoundException, match="Event not found."):
        event_service.cancel_event(sample_user, 999)


# ============================================================================
# CHECK-IN SERVICE TESTS
# ============================================================================


def test_check_in_service_init_stores_repositories(
    mock_check_in_repo: Mock, mock_event_repo: Mock
) -> None:
    """Test that init stores both repository references."""
    service = CheckInService(mock_check_in_repo, mock_event_repo)
    assert service._check_in_repo is mock_check_in_repo
    assert service._event_repo is mock_event_repo


def test_check_in_service_create_check_in_with_all_parameters_published_event(
    check_in_service: CheckInService, mock_check_in_repo: Mock, mock_event_repo: Mock, sample_published_event: Event
) -> None:
    """Test creating a check-in with all parameters for a published event."""
    mock_event_repo.get_by_id.return_value = sample_published_event
    check_in = CheckIn(
        id=1,
        visitor_name="Jane Doe",
        age=30,
        meal=True,
        dietary_preferences=[DietaryPreference.VEGAN],
        allergies="shellfish",
        event_id=2,
        user_id=uuid4(),
    )
    mock_check_in_repo.create.return_value = check_in

    result = check_in_service.create_check_in(
        2,
        visitor_name="Jane Doe",
        age=30,
        meal=True,
        dietary_preferences=[DietaryPreference.VEGAN],
        allergies="shellfish",
        user_id=uuid4(),
        require_published=True,
    )

    assert result.visitor_name == "Jane Doe"
    assert result.age == 30
    assert result.meal is True
    assert result.dietary_preferences == [DietaryPreference.VEGAN]
    assert result.allergies == "shellfish"
    assert result.event_id == 2


def test_check_in_service_create_check_in_minimal_parameters(
    check_in_service: CheckInService, mock_check_in_repo: Mock, mock_event_repo: Mock, sample_published_event: Event
) -> None:
    """Test creating a check-in with minimal parameters."""
    mock_event_repo.get_by_id.return_value = sample_published_event
    check_in = CheckIn(
        id=1,
        visitor_name="Bob Smith",
        event_id=2,
    )
    mock_check_in_repo.create.return_value = check_in

    result = check_in_service.create_check_in(
        2,
        visitor_name="Bob Smith",
    )

    assert result.visitor_name == "Bob Smith"
    assert result.age is None
    assert result.meal is False
    assert result.dietary_preferences == []
    assert result.allergies is None


def test_check_in_service_create_check_in_event_not_found_published_required(
    check_in_service: CheckInService, mock_event_repo: Mock
) -> None:
    """Test creating check-in when event doesn't exist and published is required."""
    mock_event_repo.get_by_id.return_value = None

    with pytest.raises(EventNotFoundException, match="Event not found."):
        check_in_service.create_check_in(
            999,
            visitor_name="John",
            require_published=True,
        )


def test_check_in_service_create_check_in_event_not_published(
    check_in_service: CheckInService, mock_event_repo: Mock, sample_unpublished_event: Event
) -> None:
    """Test creating check-in when event is not published but required."""
    mock_event_repo.get_by_id.return_value = sample_unpublished_event

    with pytest.raises(EventNotFoundException, match="Checkins are Closed."):
        check_in_service.create_check_in(
            3,
            visitor_name="John",
            require_published=True,
        )


def test_check_in_service_create_check_in_event_not_active(
    check_in_service: CheckInService, mock_event_repo: Mock, sample_canceled_event: Event
) -> None:
    """Test creating check-in when event is not active but required."""
    mock_event_repo.get_by_id.return_value = sample_canceled_event

    with pytest.raises(EventNotFoundException, match="Checkins are Closed."):
        check_in_service.create_check_in(
            4,
            visitor_name="John",
            require_published=True,
        )


def test_check_in_service_create_check_in_coordinator_bypass_published_check(
    check_in_service: CheckInService, mock_check_in_repo: Mock, mock_event_repo: Mock, sample_unpublished_event: Event
) -> None:
    """Test that coordinators can check in to unpublished events."""
    mock_event_repo.get_by_id.return_value = sample_unpublished_event
    check_in = CheckIn(
        id=1,
        visitor_name="Alice",
        event_id=3,
    )
    mock_check_in_repo.create.return_value = check_in

    result = check_in_service.create_check_in(
        3,
        visitor_name="Alice",
        require_published=False,
    )

    assert result.visitor_name == "Alice"


def test_check_in_service_create_check_in_dietary_preferences_default_empty(
    check_in_service: CheckInService, mock_check_in_repo: Mock, mock_event_repo: Mock, sample_published_event: Event
) -> None:
    """Test that dietary preferences default to empty list."""
    mock_event_repo.get_by_id.return_value = sample_published_event
    check_in = CheckIn(
        id=1,
        visitor_name="Charlie",
        event_id=2,
    )
    mock_check_in_repo.create.return_value = check_in

    result = check_in_service.create_check_in(
        2,
        visitor_name="Charlie",
        dietary_preferences=None,
    )

    assert result.dietary_preferences == []


def test_check_in_service_create_general_check_in_with_all_parameters(
    check_in_service: CheckInService, mock_check_in_repo: Mock
) -> None:
    """Test creating a general check-in with all parameters."""
    user_id = uuid4()
    check_in = CheckIn(
        id=1,
        visitor_name="General Visitor",
        purpose="To visit the library",
        user_id=user_id,
        event_id=None,
    )
    mock_check_in_repo.create.return_value = check_in

    result = check_in_service.create_general_check_in(
        visitor_name="General Visitor",
        purpose="To visit the library",
        user_id=user_id,
    )

    assert result.visitor_name == "General Visitor"
    assert result.purpose == "To visit the library"
    assert result.user_id == user_id
    assert result.event_id is None
    mock_check_in_repo.create.assert_called_once()


def test_check_in_service_create_general_check_in_without_user_id(
    check_in_service: CheckInService, mock_check_in_repo: Mock
) -> None:
    """Test creating a general check-in without user_id."""
    check_in = CheckIn(
        id=1,
        visitor_name="Anonymous",
        purpose="General visit",
        event_id=None,
    )
    mock_check_in_repo.create.return_value = check_in

    result = check_in_service.create_general_check_in(
        visitor_name="Anonymous",
        purpose="General visit",
    )

    assert result.visitor_name == "Anonymous"
    assert result.user_id is None
    assert result.event_id is None


def test_check_in_service_get_check_in_returns_existing_check_in(
    check_in_service: CheckInService, mock_check_in_repo: Mock, sample_check_in: CheckIn
) -> None:
    """Test retrieving an existing check-in."""
    mock_check_in_repo.get_by_id.return_value = sample_check_in

    result = check_in_service.get_check_in(1)

    assert result == sample_check_in
    mock_check_in_repo.get_by_id.assert_called_once_with(1)


def test_check_in_service_get_check_in_raises_exception_when_not_found(
    check_in_service: CheckInService, mock_check_in_repo: Mock
) -> None:
    """Test that CheckInNotFoundException is raised when check-in not found."""
    mock_check_in_repo.get_by_id.return_value = None

    with pytest.raises(CheckInNotFoundException, match="Check-in not found."):
        check_in_service.get_check_in(999)


def test_check_in_service_list_check_ins_for_existing_event(
    check_in_service: CheckInService, mock_check_in_repo: Mock, mock_event_repo: Mock, sample_event: Event, sample_check_in: CheckIn
) -> None:
    """Test listing check-ins for an existing event."""
    mock_event_repo.get_by_id.return_value = sample_event
    check_ins = [sample_check_in]
    mock_check_in_repo.list_check_ins_by_event.return_value = check_ins

    result = check_in_service.list_check_ins_for_event(1)

    assert result == check_ins
    assert len(result) == 1
    mock_check_in_repo.list_check_ins_by_event.assert_called_once_with(1)


def test_check_in_service_list_check_ins_returns_empty_list(
    check_in_service: CheckInService, mock_check_in_repo: Mock, mock_event_repo: Mock, sample_event: Event
) -> None:
    """Test listing check-ins when none exist for the event."""
    mock_event_repo.get_by_id.return_value = sample_event
    mock_check_in_repo.list_check_ins_by_event.return_value = []

    result = check_in_service.list_check_ins_for_event(1)

    assert result == []


def test_check_in_service_list_check_ins_for_nonexistent_event(
    check_in_service: CheckInService, mock_event_repo: Mock
) -> None:
    """Test listing check-ins for a non-existent event."""
    mock_event_repo.get_by_id.return_value = None

    with pytest.raises(EventNotFoundException, match="Event not found."):
        check_in_service.list_check_ins_for_event(999)


def test_check_in_service_update_check_in_all_fields(
    check_in_service: CheckInService, mock_check_in_repo: Mock, sample_check_in: CheckIn
) -> None:
    """Test updating all fields of a check-in."""
    mock_check_in_repo.get_by_id.return_value = sample_check_in
    updated_check_in = CheckIn(
        id=1,
        visitor_name="Updated Name",
        age=35,
        meal=False,
        dietary_preferences=[DietaryPreference.GLUTEN_FREE],
        allergies="dairy",
        event_id=1,
    )
    mock_check_in_repo.update.return_value = updated_check_in

    result = check_in_service.update_check_in(
        1,
        visitor_name="Updated Name",
        age=35,
        meal=False,
        dietary_preferences=[DietaryPreference.GLUTEN_FREE],
        allergies="dairy",
    )

    assert result.visitor_name == "Updated Name"
    assert result.age == 35
    assert result.meal is False
    assert result.dietary_preferences == [DietaryPreference.GLUTEN_FREE]
    assert result.allergies == "dairy"
    mock_check_in_repo.update.assert_called_once()


def test_check_in_service_update_check_in_single_field(
    check_in_service: CheckInService, mock_check_in_repo: Mock, sample_check_in: CheckIn
) -> None:
    """Test updating a single field."""
    mock_check_in_repo.get_by_id.return_value = sample_check_in
    updated_check_in = CheckIn(
        id=1,
        visitor_name="New Name",
        age=sample_check_in.age,
        meal=sample_check_in.meal,
        event_id=sample_check_in.event_id,
    )
    mock_check_in_repo.update.return_value = updated_check_in

    result = check_in_service.update_check_in(1, visitor_name="New Name")

    assert result.visitor_name == "New Name"


def test_check_in_service_update_check_in_no_fields_provided(
    check_in_service: CheckInService, mock_check_in_repo: Mock, sample_check_in: CheckIn
) -> None:
    """Test updating a check-in with no field changes."""
    mock_check_in_repo.get_by_id.return_value = sample_check_in
    mock_check_in_repo.update.return_value = sample_check_in

    result = check_in_service.update_check_in(1)

    assert result == sample_check_in
    mock_check_in_repo.update.assert_called_once()


def test_check_in_service_update_check_in_not_found(
    check_in_service: CheckInService, mock_check_in_repo: Mock
) -> None:
    """Test updating a non-existent check-in."""
    mock_check_in_repo.get_by_id.return_value = None

    with pytest.raises(CheckInNotFoundException, match="Check-in not found."):
        check_in_service.update_check_in(999, visitor_name="New Name")


def test_check_in_service_delete_check_in_existing(
    check_in_service: CheckInService, mock_check_in_repo: Mock, sample_check_in: CheckIn
) -> None:
    """Test deleting an existing check-in."""
    mock_check_in_repo.get_by_id.return_value = sample_check_in

    check_in_service.delete_check_in(1)

    mock_check_in_repo.delete.assert_called_once_with(sample_check_in)


def test_check_in_service_delete_check_in_not_found(
    check_in_service: CheckInService, mock_check_in_repo: Mock
) -> None:
    """Test deleting a non-existent check-in."""
    mock_check_in_repo.get_by_id.return_value = None

    with pytest.raises(CheckInNotFoundException, match="Check-in not found."):
        check_in_service.delete_check_in(999)
