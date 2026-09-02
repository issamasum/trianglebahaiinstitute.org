"""Tests for Check-in at TBI API routes."""

from __future__ import annotations

import uuid
from datetime import datetime
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from trianglebahaiinstitute.mytbi.checkin_at_tbi.exceptions import (
    CheckInNotFoundException,
    EventNotFoundException,
)
from trianglebahaiinstitute.mytbi.checkin_at_tbi.tables import (
    CheckIn,
    DietaryPreference,
    Event,
    EventCreationType,
    EventStatus,
)

from api.di import check_in_service_factory, event_service_factory, require_coordinator
from api.main import app
from api.models.check_in_at_tbi import CheckInResponse, EventResponse


TEST_USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
TEST_TIMESTAMP = datetime(2026, 1, 1, 12, 0, 0)


def _create_event_payload() -> dict[str, object]:
    return {
        "event_name": "Retreat",
        "start_date": "2026-01-02T09:00:00",
        "end_date": "2026-01-04T17:00:00",
        "publish": True,
    }


def _update_event_payload() -> dict[str, object]:
    return {
        "event_name": "Updated",
        "start_date": "2026-01-03T10:30:00",
        "end_date": "2026-01-04T18:00:00",
        "publish": False,
        "status": "ended",
    }


def _build_event(*, event_id: int = 1, event_name: str = "Test Event") -> Event:
    return Event(
        id=event_id,
        event_name=event_name,
        start_date=TEST_TIMESTAMP,
        end_date=TEST_TIMESTAMP,
        status=EventStatus.ACTIVE,
        publish=True,
        creation_type=EventCreationType.MANUAL,
        external_calender_id=None,
        created_by=TEST_USER_ID,
        created_at=TEST_TIMESTAMP,
        updated_by=TEST_USER_ID,
        updated_at=TEST_TIMESTAMP,
    )


def _build_check_in(
    *,
    check_in_id: int = 1,
    event_id: int | None = 1,
    purpose: str | None = None,
) -> CheckIn:
    return CheckIn(
        id=check_in_id,
        visitor_name="A Visitor",
        age=22,
        meal=True,
        dietary_preferences=[DietaryPreference.VEGAN],
        allergies="peanuts",
        event_id=event_id,
        user_id=TEST_USER_ID,
        purpose=purpose,
        checked_in_at=TEST_TIMESTAMP,
    )


def _override_admin_dependencies(
    *,
    event_svc: MagicMock | None = None,
    check_in_svc: MagicMock | None = None,
) -> object:
    subject = object()
    app.dependency_overrides[require_coordinator] = lambda: subject
    if event_svc is not None:
        app.dependency_overrides[event_service_factory] = lambda: event_svc
    if check_in_svc is not None:
        app.dependency_overrides[check_in_service_factory] = lambda: check_in_svc
    return subject


def _event_response_payload(event: Event) -> dict[str, object]:
    return EventResponse.model_validate(event).model_dump(mode="json")


def _check_in_response_payload(check_in: CheckIn) -> dict[str, object]:
    return CheckInResponse.model_validate(check_in).model_dump(mode="json")


def test_admin_create_event(client: TestClient) -> None:
    # Arrange
    event_svc = MagicMock()
    event_svc.create_event.return_value = _build_event(
        event_id=10, event_name="Retreat"
    )
    subject = _override_admin_dependencies(event_svc=event_svc)
    payload = _create_event_payload()

    # Act
    response = client.post(
        "/api/admin/check-in/events",
        json=payload,
    )

    # Assert
    assert response.status_code == 201
    assert response.json() == _event_response_payload(
        event_svc.create_event.return_value
    )
    event_svc.create_event.assert_called_once_with(
        subject,
        event_name="Retreat",
        start_date=datetime(2026, 1, 2, 9, 0, 0),
        end_date=datetime(2026, 1, 4, 17, 0, 0),
        publish=True,
    )


def test_admin_analyze_all_events_returns_null_payload(client: TestClient) -> None:
    # Arrange
    # No special dependencies needed.

    # Act
    response = client.get("/api/admin/check-in/events/analysis")

    # Assert
    assert response.status_code == 200
    assert response.json() is None


def test_admin_analyze_event_returns_null_payload(client: TestClient) -> None:
    # Arrange
    # No special dependencies needed.

    # Act
    response = client.get("/api/admin/check-in/events/1/analysis")

    # Assert
    assert response.status_code == 200
    assert response.json() is None


def test_admin_list_events(client: TestClient) -> None:
    # Arrange
    event_svc = MagicMock()
    event_svc.list_events.return_value = [
        _build_event(event_id=1),
        _build_event(event_id=2),
    ]
    _override_admin_dependencies(event_svc=event_svc)

    # Act
    response = client.get("/api/admin/check-in/events")

    # Assert
    assert response.status_code == 200
    assert response.json() == [
        _event_response_payload(event) for event in event_svc.list_events.return_value
    ]
    event_svc.list_events.assert_called_once_with()


def test_admin_get_event(client: TestClient) -> None:
    # Arrange
    event_svc = MagicMock()
    event_svc.get_event.return_value = _build_event(event_id=77)
    _override_admin_dependencies(event_svc=event_svc)

    # Act
    response = client.get("/api/admin/check-in/events/77")

    # Assert
    assert response.status_code == 200
    assert response.json() == _event_response_payload(event_svc.get_event.return_value)
    event_svc.get_event.assert_called_once_with(77)


def test_admin_get_event_not_found(client: TestClient) -> None:
    # Arrange
    event_svc = MagicMock()
    event_svc.get_event.side_effect = EventNotFoundException
    _override_admin_dependencies(event_svc=event_svc)

    # Act
    response = client.get("/api/admin/check-in/events/123")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Event not found."}


def test_admin_update_event(client: TestClient) -> None:
    # Arrange
    event_svc = MagicMock()
    event_svc.update_event.return_value = _build_event(event_id=8, event_name="Updated")
    subject = _override_admin_dependencies(event_svc=event_svc)
    payload = _update_event_payload()

    # Act
    response = client.patch(
        "/api/admin/check-in/events/8",
        json=payload,
    )

    # Assert
    assert response.status_code == 201
    assert response.json() == _event_response_payload(
        event_svc.update_event.return_value
    )
    event_svc.update_event.assert_called_once_with(
        subject,
        8,
        event_name="Updated",
        start_date=datetime(2026, 1, 3, 10, 30, 0),
        end_date=datetime(2026, 1, 4, 18, 0, 0),
        publish=False,
        status=EventStatus.ENDED,
    )


def test_admin_update_event_not_found(client: TestClient) -> None:
    # Arrange
    event_svc = MagicMock()
    event_svc.update_event.side_effect = EventNotFoundException
    _override_admin_dependencies(event_svc=event_svc)

    # Act
    response = client.patch(
        "/api/admin/check-in/events/8", json={"event_name": "Updated"}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Event not found."}


def test_admin_delete_event(client: TestClient) -> None:
    # Arrange
    event_svc = MagicMock()
    subject = _override_admin_dependencies(event_svc=event_svc)

    # Act
    response = client.delete("/api/admin/check-in/events/22")

    # Assert
    assert response.status_code == 204
    event_svc.cancel_event.assert_called_once_with(subject, 22)


def test_admin_delete_event_not_found(client: TestClient) -> None:
    # Arrange
    event_svc = MagicMock()
    event_svc.cancel_event.side_effect = EventNotFoundException
    _override_admin_dependencies(event_svc=event_svc)

    # Act
    response = client.delete("/api/admin/check-in/events/22")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Event not found."}


def test_admin_create_check_in(client: TestClient) -> None:
    # Arrange
    check_in_svc = MagicMock()
    check_in_svc.create_check_in.return_value = _build_check_in(
        check_in_id=5, event_id=2
    )
    _override_admin_dependencies(check_in_svc=check_in_svc)

    # Act
    response = client.post(
        "/api/admin/check-in/events/2/check-ins",
        json={
            "visitor_name": "A Visitor",
            "age": 22,
            "meal": True,
            "dietary_preferences": ["vegan"],
            "allergies": "peanuts",
        },
    )

    # Assert
    assert response.status_code == 201
    assert response.json() == _check_in_response_payload(
        check_in_svc.create_check_in.return_value
    )
    check_in_svc.create_check_in.assert_called_once_with(
        2,
        visitor_name="A Visitor",
        age=22,
        meal=True,
        dietary_preferences=[DietaryPreference.VEGAN],
        allergies="peanuts",
        require_published=False,
    )


def test_admin_create_check_in_event_not_found(client: TestClient) -> None:
    # Arrange
    check_in_svc = MagicMock()
    check_in_svc.create_check_in.side_effect = EventNotFoundException
    _override_admin_dependencies(check_in_svc=check_in_svc)

    # Act
    response = client.post(
        "/api/admin/check-in/events/2/check-ins",
        json={"visitor_name": "A Visitor"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Event not found."}


def test_admin_list_check_ins(client: TestClient) -> None:
    # Arrange
    check_in_svc = MagicMock()
    check_in_svc.list_check_ins_for_event.return_value = [
        _build_check_in(check_in_id=1),
        _build_check_in(check_in_id=2),
    ]
    _override_admin_dependencies(check_in_svc=check_in_svc)

    # Act
    response = client.get("/api/admin/check-in/events/1/check-ins")

    # Assert
    assert response.status_code == 200
    assert response.json() == [
        _check_in_response_payload(check_in)
        for check_in in check_in_svc.list_check_ins_for_event.return_value
    ]
    check_in_svc.list_check_ins_for_event.assert_called_once_with(1)


def test_admin_list_check_ins_event_not_found(client: TestClient) -> None:
    # Arrange
    check_in_svc = MagicMock()
    check_in_svc.list_check_ins_for_event.side_effect = EventNotFoundException
    _override_admin_dependencies(check_in_svc=check_in_svc)

    # Act
    response = client.get("/api/admin/check-in/events/1/check-ins")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Event not found."}


def test_admin_get_check_in(client: TestClient) -> None:
    # Arrange
    check_in_svc = MagicMock()
    check_in_svc.get_check_in_for_event.return_value = _build_check_in(check_in_id=6)
    _override_admin_dependencies(check_in_svc=check_in_svc)

    # Act
    response = client.get("/api/admin/check-in/events/1/check-ins/6")

    # Assert
    assert response.status_code == 200
    assert response.json() == _check_in_response_payload(
        check_in_svc.get_check_in_for_event.return_value
    )
    check_in_svc.get_check_in_for_event.assert_called_once_with(1, 6)


def test_admin_get_check_in_not_found(client: TestClient) -> None:
    # Arrange
    check_in_svc = MagicMock()
    check_in_svc.get_check_in_for_event.side_effect = CheckInNotFoundException
    _override_admin_dependencies(check_in_svc=check_in_svc)

    # Act
    response = client.get("/api/admin/check-in/events/1/check-ins/6")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Check-in not found."}


def test_admin_update_check_in(client: TestClient) -> None:
    # Arrange
    check_in_svc = MagicMock()
    check_in_svc.get_check_in_for_event.return_value = _build_check_in(check_in_id=3)
    check_in_svc.update_check_in.return_value = _build_check_in(check_in_id=3)
    _override_admin_dependencies(check_in_svc=check_in_svc)

    # Act
    response = client.patch(
        "/api/admin/check-in/events/1/check-ins/3",
        json={"visitor_name": "Updated Name", "meal": False},
    )

    # Assert
    assert response.status_code == 201
    assert response.json() == _check_in_response_payload(
        check_in_svc.update_check_in.return_value
    )
    check_in_svc.get_check_in_for_event.assert_called_once_with(1, 3)
    check_in_svc.update_check_in.assert_called_once_with(
        3,
        visitor_name="Updated Name",
        meal=False,
    )


def test_admin_update_check_in_not_found(client: TestClient) -> None:
    # Arrange
    check_in_svc = MagicMock()
    check_in_svc.get_check_in_for_event.side_effect = CheckInNotFoundException
    _override_admin_dependencies(check_in_svc=check_in_svc)

    # Act
    response = client.patch(
        "/api/admin/check-in/events/1/check-ins/3",
        json={"visitor_name": "Updated Name"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Check-in not found."}
    check_in_svc.update_check_in.assert_not_called()


def test_admin_delete_check_in(client: TestClient) -> None:
    # Arrange
    check_in_svc = MagicMock()
    check_in_svc.get_check_in_for_event.return_value = _build_check_in(check_in_id=9)
    _override_admin_dependencies(check_in_svc=check_in_svc)

    # Act
    response = client.delete("/api/admin/check-in/events/1/check-ins/9")

    # Assert
    assert response.status_code == 201
    check_in_svc.get_check_in_for_event.assert_called_once_with(1, 9)
    check_in_svc.delete_check_in.assert_called_once_with(9)


def test_admin_delete_check_in_not_found(client: TestClient) -> None:
    # Arrange
    check_in_svc = MagicMock()
    check_in_svc.get_check_in_for_event.side_effect = CheckInNotFoundException
    _override_admin_dependencies(check_in_svc=check_in_svc)

    # Act
    response = client.delete("/api/admin/check-in/events/1/check-ins/9")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Check-in not found."}
    check_in_svc.delete_check_in.assert_not_called()


def test_admin_create_general_check_in(client: TestClient) -> None:
    # Arrange
    check_in_svc = MagicMock()
    check_in_svc.create_general_check_in.return_value = _build_check_in(
        check_in_id=11,
        event_id=None,
        purpose="meeting",
    )
    _override_admin_dependencies(check_in_svc=check_in_svc)

    # Act
    response = client.post(
        "/api/admin/check-in/general/check-ins",
        json={"visitor_name": "A Visitor", "purpose": "meeting"},
    )

    # Assert
    assert response.status_code == 201
    assert response.json() == _check_in_response_payload(
        check_in_svc.create_general_check_in.return_value
    )
    check_in_svc.create_general_check_in.assert_called_once_with(
        visitor_name="A Visitor",
        purpose="meeting",
    )


def test_public_list_events(client: TestClient) -> None:
    # Arrange
    event_svc = MagicMock()
    event_svc.list_published_events.return_value = [_build_event(event_id=4)]
    app.dependency_overrides[event_service_factory] = lambda: event_svc

    # Act
    response = client.get("/api/check-in/events")

    # Assert
    assert response.status_code == 200
    assert response.json() == [
        _event_response_payload(event)
        for event in event_svc.list_published_events.return_value
    ]
    event_svc.list_published_events.assert_called_once_with()


def test_public_get_event(client: TestClient) -> None:
    # Arrange
    event_svc = MagicMock()
    event_svc.get_published_event.return_value = _build_event(event_id=5)
    app.dependency_overrides[event_service_factory] = lambda: event_svc

    # Act
    response = client.get("/api/check-in/events/5")

    # Assert
    assert response.status_code == 200
    assert response.json() == _event_response_payload(
        event_svc.get_published_event.return_value
    )
    event_svc.get_published_event.assert_called_once_with(5)


def test_public_get_event_not_found(client: TestClient) -> None:
    # Arrange
    event_svc = MagicMock()
    event_svc.get_published_event.side_effect = EventNotFoundException
    app.dependency_overrides[event_service_factory] = lambda: event_svc

    # Act
    response = client.get("/api/check-in/events/5")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Event not found."}


def test_public_create_check_in(client: TestClient) -> None:
    # Arrange
    check_in_svc = MagicMock()
    check_in_svc.create_check_in.return_value = _build_check_in(
        check_in_id=12, event_id=5
    )
    app.dependency_overrides[check_in_service_factory] = lambda: check_in_svc

    # Act
    response = client.post(
        "/api/check-in/events/5/check-ins",
        json={"visitor_name": "A Visitor", "meal": False},
    )

    # Assert
    assert response.status_code == 201
    assert response.json() == _check_in_response_payload(
        check_in_svc.create_check_in.return_value
    )
    check_in_svc.create_check_in.assert_called_once_with(
        5,
        visitor_name="A Visitor",
        age=None,
        meal=False,
        dietary_preferences=[],
        allergies=None,
    )


def test_public_create_check_in_event_not_found(client: TestClient) -> None:
    # Arrange
    check_in_svc = MagicMock()
    check_in_svc.create_check_in.side_effect = EventNotFoundException
    app.dependency_overrides[check_in_service_factory] = lambda: check_in_svc

    # Act
    response = client.post(
        "/api/check-in/events/5/check-ins",
        json={"visitor_name": "A Visitor"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Event not found."}


def test_public_create_general_check_in(client: TestClient) -> None:
    # Arrange
    check_in_svc = MagicMock()
    check_in_svc.create_general_check_in.return_value = _build_check_in(
        check_in_id=13,
        event_id=None,
        purpose="tour",
    )
    app.dependency_overrides[check_in_service_factory] = lambda: check_in_svc

    # Act
    response = client.post(
        "/api/check-in/general/check-ins",
        json={"visitor_name": "A Visitor", "purpose": "tour"},
    )

    # Assert
    assert response.status_code == 201
    assert response.json() == _check_in_response_payload(
        check_in_svc.create_general_check_in.return_value
    )
    check_in_svc.create_general_check_in.assert_called_once_with(
        visitor_name="A Visitor",
        purpose="tour",
    )
