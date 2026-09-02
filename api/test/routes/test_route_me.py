from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from trianglebahaiinstitute.tables.user import User, UserRole

from api.di import get_authenticated_user, user_repository_factory
from api.main import app
from api.models import UpdateProfileRequest, UserProfile
from api.routes.me import get_current_subject_profile, update_current_subject_profile


def _stub_user(
    *,
    user_id: uuid.UUID | None = None,
    email: str = "user@example.com",
    first_name: str = "Test",
    last_name: str = "User",
    phone: str | None = "919-111-1000",
) -> User:
    return User(
        id=user_id or uuid.UUID("11111111-1111-1111-1111-111111111111"),
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        password_hash="hashed",
        role=UserRole.COORDINATOR,
        is_active=True,
    )


# Unit tests


def test_get_current_subject_profile_returns_profile() -> None:
    # Arrange
    subject = _stub_user()

    # Act
    result = get_current_subject_profile(subject)

    # Assert
    assert isinstance(result, UserProfile)
    assert result.id == subject.id
    assert result.first_name == "Test"
    assert result.last_name == "User"
    assert result.email == "user@example.com"


def test_update_current_subject_profile_updates_non_email_fields() -> None:
    # Arrange
    subject = _stub_user()
    user_repo = MagicMock()
    user_repo.update_user.return_value = subject
    payload = UpdateProfileRequest(first_name="Updated", phone="919-123-1234")

    # Act
    result = update_current_subject_profile(subject, payload, user_repo)

    # Assert
    assert result.first_name == "Updated"
    assert result.phone == "919-123-1234"
    user_repo.get_by_email.assert_not_called()
    user_repo.update_user.assert_called_once_with(subject)


def test_update_current_subject_profile_skips_lookup_for_same_email() -> None:
    # Arrange
    subject = _stub_user(email="same@example.com")
    user_repo = MagicMock()
    user_repo.update_user.return_value = subject
    payload = UpdateProfileRequest(email="same@example.com")

    # Act
    result = update_current_subject_profile(subject, payload, user_repo)

    # Assert
    assert result.email == "same@example.com"
    user_repo.get_by_email.assert_not_called()
    user_repo.update_user.assert_called_once_with(subject)


def test_update_current_subject_profile_updates_when_email_is_available() -> None:
    # Arrange
    subject = _stub_user(email="old@example.com")
    user_repo = MagicMock()
    user_repo.get_by_email.return_value = None
    user_repo.update_user.return_value = subject
    payload = UpdateProfileRequest(email="new@example.com")

    # Act
    result = update_current_subject_profile(subject, payload, user_repo)

    # Assert
    assert result.email == "new@example.com"
    user_repo.get_by_email.assert_called_once_with("new@example.com")
    user_repo.update_user.assert_called_once_with(subject)


def test_update_current_subject_profile_updates_when_email_belongs_to_subject() -> None:
    # Arrange
    subject = _stub_user(
        user_id=uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        email="old@example.com",
    )
    existing = _stub_user(
        user_id=uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        email="new@example.com",
    )
    user_repo = MagicMock()
    user_repo.get_by_email.return_value = existing
    user_repo.update_user.return_value = subject
    payload = UpdateProfileRequest(email="new@example.com")

    # Act
    result = update_current_subject_profile(subject, payload, user_repo)

    # Assert
    assert result.email == "new@example.com"
    user_repo.get_by_email.assert_called_once_with("new@example.com")
    user_repo.update_user.assert_called_once_with(subject)


def test_update_current_subject_profile_raises_409_for_taken_email() -> None:
    # Arrange
    subject = _stub_user(
        user_id=uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        email="old@example.com",
    )
    existing = _stub_user(
        user_id=uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        email="taken@example.com",
    )
    user_repo = MagicMock()
    user_repo.get_by_email.return_value = existing
    payload = UpdateProfileRequest(email="taken@example.com")

    # Act / Assert
    with pytest.raises(HTTPException) as exc_info:
        update_current_subject_profile(subject, payload, user_repo)

    exc = exc_info.value
    assert exc.status_code == 409
    assert exc.detail == "Email already in use."
    user_repo.update_user.assert_not_called()


# ----- Integration tests ---------


@pytest.mark.integration
def test_me_endpoint_returns_current_profile(client: TestClient) -> None:
    # Arrange
    app.dependency_overrides[get_authenticated_user] = lambda: _stub_user(
        email="profile@example.com"
    )

    # Act
    response = client.get("/api/mytbi/me")

    # Assert
    assert response.status_code == 200
    assert response.json()["email"] == "profile@example.com"
    assert response.json()["first_name"] == "Test"


@pytest.mark.integration
def test_patch_me_endpoint_updates_profile(client: TestClient) -> None:
    # Arrange
    subject = _stub_user(email="before@example.com", first_name="Before")
    user_repo = MagicMock()
    user_repo.get_by_email.return_value = None
    user_repo.update_user.return_value = subject
    app.dependency_overrides[get_authenticated_user] = lambda: subject
    app.dependency_overrides[user_repository_factory] = lambda: user_repo

    # Act
    response = client.patch(
        "/api/mytbi/me",
        json={"email": "after@example.com", "first_name": "After"},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["email"] == "after@example.com"
    assert response.json()["first_name"] == "After"


@pytest.mark.integration
def test_patch_me_endpoint_returns_409_when_email_is_taken(client: TestClient) -> None:
    # Arrange
    subject = _stub_user(
        user_id=uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        email="before@example.com",
    )
    taken_user = _stub_user(
        user_id=uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        email="taken@example.com",
    )
    user_repo = MagicMock()
    user_repo.get_by_email.return_value = taken_user
    app.dependency_overrides[get_authenticated_user] = lambda: subject
    app.dependency_overrides[user_repository_factory] = lambda: user_repo

    # Act
    response = client.patch("/api/mytbi/me", json={"email": "taken@example.com"})

    # Assert
    assert response.status_code == 409
    assert response.json() == {"detail": "Email already in use."}
    user_repo.update_user.assert_not_called()
