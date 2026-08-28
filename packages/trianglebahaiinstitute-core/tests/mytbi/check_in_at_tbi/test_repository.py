# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Integration tests for Check-in at TBI repository."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlmodel import Session

from trianglebahaiinstitute.mytbi.checkin_at_tbi.repository import (
    CheckInRepository,
    EventRepository,
)
from trianglebahaiinstitute.mytbi.checkin_at_tbi.tables import (
    CheckIn,
    DietaryPreference,
    Event,
    EventCreationType,
    EventStatus,
)
from trianglebahaiinstitute.tables.user import User


@pytest.fixture()
def user(session: Session) -> User:
    """Create a test user for event ownership."""
    user = User(
        first_name="Test",
        last_name="Coordinator",
        phone="919-111-1111",
        email="coordinator@example.com",
    )
    session.add(user)
    session.flush()
    return user


@pytest.fixture()
def sample_event(session: Session, user: User) -> Event:
    """Create a sample event for testing."""
    event = Event(
        event_name="Sample Event",
        start_date=datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc),
        end_date=datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc),
        status=EventStatus.ACTIVE,
        publish=True,
        creation_type=EventCreationType.MANUAL,
        created_by=user.id,
        updated_by=user.id,
    )
    session.add(event)
    session.flush()
    return event


# ---- EventRepository Tests ----


@pytest.mark.integration
def test_event_repository_create_persists_event(session: Session, user: User) -> None:
    """Test creating and persisting an event."""
    # Arrange
    repo = EventRepository(session)
    event = Event(
        event_name="New Event",
        start_date=datetime(2026, 10, 1, 14, 0, tzinfo=timezone.utc),
        end_date=datetime(2026, 10, 1, 16, 0, tzinfo=timezone.utc),
        status=EventStatus.ACTIVE,
        publish=True,
        creation_type=EventCreationType.MANUAL,
        created_by=user.id,
        updated_by=user.id,
    )

    # Act
    result = repo.create(event)

    # Assert
    assert result.id is not None
    assert result.event_name == "New Event"
    persisted = repo.get_by_id(result.id)
    assert persisted is not None
    assert persisted.event_name == "New Event"


@pytest.mark.integration
def test_event_repository_get_by_id_returns_none_when_not_found(
    session: Session,
) -> None:
    """Test getting event by ID when it doesn't exist."""
    # Arrange
    repo = EventRepository(session)

    # Act
    result = repo.get_by_id(9999)

    # Assert
    assert result is None


@pytest.mark.integration
def test_event_repository_get_by_id_returns_event_when_found(
    session: Session, sample_event: Event
) -> None:
    """Test getting event by ID when it exists."""
    # Arrange
    repo = EventRepository(session)

    # Act
    result = repo.get_by_id(sample_event.id)

    # Assert
    assert result is not None
    assert result.id == sample_event.id
    assert result.event_name == "Sample Event"


@pytest.mark.integration
def test_event_repository_list_events_returns_empty_when_no_events(
    session: Session,
) -> None:
    """Test listing events when none exist."""
    # Arrange
    repo = EventRepository(session)

    # Act
    result = repo.list_events()

    # Assert
    assert result == []


@pytest.mark.integration
def test_event_repository_list_events_returns_all_events(
    session: Session, user: User
) -> None:
    """Test listing all events."""
    # Arrange
    repo = EventRepository(session)
    event1 = Event(
        event_name="Event One",
        start_date=datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc),
        end_date=datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc),
        status=EventStatus.ACTIVE,
        publish=True,
        creation_type=EventCreationType.MANUAL,
        created_by=user.id,
        updated_by=user.id,
    )
    event2 = Event(
        event_name="Event Two",
        start_date=datetime(2026, 9, 2, 10, 0, tzinfo=timezone.utc),
        end_date=datetime(2026, 9, 2, 12, 0, tzinfo=timezone.utc),
        status=EventStatus.ACTIVE,
        publish=True,
        creation_type=EventCreationType.MANUAL,
        created_by=user.id,
        updated_by=user.id,
    )
    session.add(event1)
    session.add(event2)
    session.flush()

    # Act
    result = repo.list_events()

    # Assert
    assert len(result) == 2
    assert any(e.event_name == "Event One" for e in result)
    assert any(e.event_name == "Event Two" for e in result)


@pytest.mark.integration
def test_event_repository_lists_published_active_events_returns_only_matching(
    session: Session, user: User
) -> None:
    """Test listing only published and active events."""
    # Arrange
    repo = EventRepository(session)
    # Create published active event
    active_event = Event(
        event_name="Active Published Event",
        start_date=datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc),
        end_date=datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc),
        status=EventStatus.ACTIVE,
        publish=True,
        creation_type=EventCreationType.MANUAL,
        created_by=user.id,
        updated_by=user.id,
    )
    # Create unpublished active event
    unpublished_event = Event(
        event_name="Unpublished Active Event",
        start_date=datetime(2026, 9, 2, 10, 0, tzinfo=timezone.utc),
        end_date=datetime(2026, 9, 2, 12, 0, tzinfo=timezone.utc),
        status=EventStatus.ACTIVE,
        publish=False,
        creation_type=EventCreationType.MANUAL,
        created_by=user.id,
        updated_by=user.id,
    )
    # Create published canceled event
    canceled_event = Event(
        event_name="Published Canceled Event",
        start_date=datetime(2026, 9, 3, 10, 0, tzinfo=timezone.utc),
        end_date=datetime(2026, 9, 3, 12, 0, tzinfo=timezone.utc),
        status=EventStatus.CANCELED,
        publish=True,
        creation_type=EventCreationType.MANUAL,
        created_by=user.id,
        updated_by=user.id,
    )
    session.add(active_event)
    session.add(unpublished_event)
    session.add(canceled_event)
    session.flush()

    # Act
    result = repo.lists_published_active_events()

    # Assert
    assert len(result) == 1
    assert result[0].event_name == "Active Published Event"
    assert result[0].publish is True
    assert result[0].status == EventStatus.ACTIVE


@pytest.mark.integration
def test_event_repository_cancel_event_updates_status(
    session: Session, sample_event: Event
) -> None:
    """Test canceling an event."""
    # Arrange
    repo = EventRepository(session)
    assert sample_event.status == EventStatus.ACTIVE

    # Act
    result = repo.cancel_event(sample_event)

    # Assert
    assert result.status == EventStatus.CANCELED
    # Verify persistence
    persisted = repo.get_by_id(sample_event.id)
    assert persisted is not None
    assert persisted.status == EventStatus.CANCELED


@pytest.mark.integration
def test_event_repository_update_modifies_event(
    session: Session, sample_event: Event
) -> None:
    """Test updating an event."""
    # Arrange
    repo = EventRepository(session)
    sample_event.event_name = "Updated Event Name"

    # Act
    result = repo.update(sample_event)

    # Assert
    assert result.event_name == "Updated Event Name"
    persisted = repo.get_by_id(sample_event.id)
    assert persisted is not None
    assert persisted.event_name == "Updated Event Name"


# ---- CheckInRepository Tests ----


@pytest.mark.integration
def test_check_in_repository_create_persists_check_in(
    session: Session, sample_event: Event
) -> None:
    """Test creating and persisting a check-in."""
    # Arrange
    repo = CheckInRepository(session)
    check_in = CheckIn(
        visitor_name="John Doe",
        age=30,
        meal=True,
        dietary_preferences=[DietaryPreference.VEGETARIAN],
        allergies=None,
        purpose="Learning",
        event_id=sample_event.id,
    )

    # Act
    result = repo.create(check_in)

    # Assert
    assert result.id is not None
    assert result.visitor_name == "John Doe"
    persisted = repo.get_by_id(result.id)
    assert persisted is not None
    assert persisted.visitor_name == "John Doe"
    assert persisted.age == 30
    assert persisted.meal is True


@pytest.mark.integration
def test_check_in_repository_get_by_id_returns_none_when_not_found(
    session: Session,
) -> None:
    """Test getting check-in by ID when it doesn't exist."""
    # Arrange
    repo = CheckInRepository(session)

    # Act
    result = repo.get_by_id(9999)

    # Assert
    assert result is None


@pytest.mark.integration
def test_check_in_repository_get_by_id_returns_check_in_when_found(
    session: Session, sample_event: Event
) -> None:
    """Test getting check-in by ID when it exists."""
    # Arrange
    repo = CheckInRepository(session)
    check_in = CheckIn(
        visitor_name="Jane Smith",
        age=25,
        meal=False,
        dietary_preferences=[DietaryPreference.GLUTEN_FREE, DietaryPreference.VEGAN],
        allergies="Peanuts",
        purpose="Attending",
        event_id=sample_event.id,
    )
    session.add(check_in)
    session.flush()

    # Act
    result = repo.get_by_id(check_in.id)

    # Assert
    assert result is not None
    assert result.id == check_in.id
    assert result.visitor_name == "Jane Smith"
    assert result.allergies == "Peanuts"
    assert DietaryPreference.VEGAN in result.dietary_preferences


@pytest.mark.integration
def test_check_in_repository_list_check_ins_by_event_returns_empty_when_no_check_ins(
    session: Session, sample_event: Event
) -> None:
    """Test listing check-ins for an event with no check-ins."""
    # Arrange
    repo = CheckInRepository(session)

    # Act
    result = repo.list_check_ins_by_event(sample_event.id)

    # Assert
    assert result == []


@pytest.mark.integration
def test_check_in_repository_list_check_ins_by_event_returns_all_for_event(
    session: Session, user: User
) -> None:
    """Test listing all check-ins for a specific event."""
    # Arrange
    repo = CheckInRepository(session)
    event1 = Event(
        event_name="Event 1",
        status=EventStatus.ACTIVE,
        publish=True,
        creation_type=EventCreationType.MANUAL,
        created_by=user.id,
        updated_by=user.id,
    )
    event2 = Event(
        event_name="Event 2",
        status=EventStatus.ACTIVE,
        publish=True,
        creation_type=EventCreationType.MANUAL,
        created_by=user.id,
        updated_by=user.id,
    )
    session.add(event1)
    session.add(event2)
    session.flush()

    check_in1 = CheckIn(
        visitor_name="Visitor 1", meal=True, event_id=event1.id
    )
    check_in2 = CheckIn(
        visitor_name="Visitor 2", meal=False, event_id=event1.id
    )
    check_in3 = CheckIn(
        visitor_name="Visitor 3", meal=True, event_id=event2.id
    )
    session.add(check_in1)
    session.add(check_in2)
    session.add(check_in3)
    session.flush()

    # Act
    result = repo.list_check_ins_by_event(event1.id)

    # Assert
    assert len(result) == 2
    assert all(ci.event_id == event1.id for ci in result)
    assert any(ci.visitor_name == "Visitor 1" for ci in result)
    assert any(ci.visitor_name == "Visitor 2" for ci in result)


@pytest.mark.integration
def test_check_in_repository_list_check_ins_by_event_filters_correctly(
    session: Session, user: User
) -> None:
    """Test that listing check-ins only returns those for the specified event."""
    # Arrange
    repo = CheckInRepository(session)
    event = Event(
        event_name="Test Event",
        status=EventStatus.ACTIVE,
        publish=True,
        creation_type=EventCreationType.MANUAL,
        created_by=user.id,
        updated_by=user.id,
    )
    session.add(event)
    session.flush()

    check_in_for_event = CheckIn(
        visitor_name="Event Visitor", event_id=event.id
    )
    check_in_no_event = CheckIn(visitor_name="No Event Visitor", event_id=None)
    session.add(check_in_for_event)
    session.add(check_in_no_event)
    session.flush()

    # Act
    result = repo.list_check_ins_by_event(event.id)

    # Assert
    assert len(result) == 1
    assert result[0].visitor_name == "Event Visitor"


@pytest.mark.integration
def test_check_in_repository_update_modifies_check_in(
    session: Session, sample_event: Event
) -> None:
    """Test updating a check-in."""
    # Arrange
    repo = CheckInRepository(session)
    check_in = CheckIn(
        visitor_name="Original Name",
        age=20,
        meal=False,
        event_id=sample_event.id,
    )
    session.add(check_in)
    session.flush()

    check_in.visitor_name = "Updated Name"
    check_in.age = 25
    check_in.meal = True

    # Act
    result = repo.update(check_in)

    # Assert
    assert result.visitor_name == "Updated Name"
    assert result.age == 25
    assert result.meal is True
    persisted = repo.get_by_id(check_in.id)
    assert persisted is not None
    assert persisted.visitor_name == "Updated Name"
    assert persisted.age == 25


@pytest.mark.integration
def test_check_in_repository_handles_dietary_preferences(
    session: Session, sample_event: Event
) -> None:
    """Test check-in with multiple dietary preferences."""
    # Arrange
    repo = CheckInRepository(session)
    check_in = CheckIn(
        visitor_name="Special Diet Visitor",
        dietary_preferences=[
            DietaryPreference.VEGAN,
            DietaryPreference.GLUTEN_FREE,
            DietaryPreference.HALAL,
        ],
        event_id=sample_event.id,
    )

    # Act
    result = repo.create(check_in)

    # Assert
    assert len(result.dietary_preferences) == 3
    assert DietaryPreference.VEGAN in result.dietary_preferences
    assert DietaryPreference.GLUTEN_FREE in result.dietary_preferences
    assert DietaryPreference.HALAL in result.dietary_preferences


@pytest.mark.integration
def test_check_in_repository_handles_optional_fields(
    session: Session, sample_event: Event
) -> None:
    """Test check-in with minimal required fields."""
    # Arrange
    repo = CheckInRepository(session)
    check_in = CheckIn(visitor_name="Minimal Visitor", event_id=sample_event.id)

    # Act
    result = repo.create(check_in)

    # Assert
    assert result.id is not None
    assert result.visitor_name == "Minimal Visitor"
    assert result.age is None
    assert result.meal is False
    assert result.allergies is None
    assert result.purpose is None
    assert result.user_id is None
