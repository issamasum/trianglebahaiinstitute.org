from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from trianglebahaiinstitute.services.auth_service import (
    AuthenticationException,
    AuthService,
)
from trianglebahaiinstitute.tables.user import User, UserRole

from api import di


def _user(*, role: UserRole = UserRole.COORDINATOR) -> User:
    user = MagicMock(spec=User)
    user.role = role
    return user


def test_auth_service_factory_returns_auth_service_instance() -> None:
    # Arrange
    settings = MagicMock()
    user_repo = MagicMock()

    # Act
    result = di.auth_service_factory(settings, user_repo)

    # Assert
    assert isinstance(result, AuthService)


def test_settings_factory_returns_settings_from_provider() -> None:
    # Act
    with patch("api.di.get_settings", return_value="settings") as get_settings_mock:
        result = di.settings_factory()

    # Assert
    assert result == "settings"
    get_settings_mock.assert_called_once_with()


def test_user_repository_factory_builds_repository() -> None:
    # Arrange
    session = MagicMock()

    # Act
    repo = di.user_repository_factory(session)

    # Assert
    assert repo._session is session


def test_get_authenticated_user_returns_subject_on_valid_token() -> None:
    # Arrange
    auth_svc = MagicMock()
    auth_svc.verify_jwt.return_value = "user-id"
    user = _user()
    auth_svc.get_user_by_id.return_value = user
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="valid-token"
    )

    # Act
    result = di.get_authenticated_user(auth_svc, credentials)

    # Assert
    assert result is user


def test_get_authenticated_user_raises_401_on_invalid_token() -> None:
    # Arrange
    auth_svc = MagicMock()
    auth_svc.verify_jwt.side_effect = AuthenticationException("invalid")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad-token")

    # Act / Assert
    with pytest.raises(HTTPException, match="Invalid or expired token.") as exc_info:
        di.get_authenticated_user(auth_svc, credentials)

    assert exc_info.value.status_code == 401


def test_get_authenticated_user_raises_401_when_subject_missing() -> None:
    # Arrange
    auth_svc = MagicMock()
    auth_svc.verify_jwt.return_value = "user-id"
    auth_svc.get_user_by_id.return_value = None
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="valid-token"
    )

    # Act / Assert
    with pytest.raises(HTTPException, match="User not found.") as exc_info:
        di.get_authenticated_user(auth_svc, credentials)

    assert exc_info.value.status_code == 401


def test_require_coordinator_returns_user_when_role_matches() -> None:
    # Arrange
    user = _user(role=UserRole.COORDINATOR)

    # Act
    result = di.require_coordinator(user)

    # Assert
    assert result is user


def test_require_coordinator_raises_403_when_role_does_not_match() -> None:
    # Arrange
    user = MagicMock(spec=User)
    user.role = "visitor"

    # Act / Assert
    with pytest.raises(HTTPException, match="Coordinator access required.") as exc_info:
        di.require_coordinator(user)

    assert exc_info.value.status_code == 403


def test_event_and_check_in_factories_build_dependencies() -> None:
    # Arrange
    session = MagicMock()
    event_repo = di.event_repository_factory(session)
    check_in_repo = di.check_in_repository_factory(session)

    # Act
    event_service = di.event_service_factory(event_repo)
    check_in_service = di.check_in_service_factory(check_in_repo, event_repo)

    # Assert
    assert event_repo._session is session
    assert check_in_repo._session is session
    assert event_service._event_repo is event_repo
    assert check_in_service._event_repo is event_repo
    assert check_in_service._check_in_repo is check_in_repo
