from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import jwt
import pytest

from trianglebahaiinstitute.config import Settings
from trianglebahaiinstitute.services.auth_service import (
    AuthenticationException,
    AuthService,
    WeakPasswordException,
)
from trianglebahaiinstitute.tables.user import User, UserRole


def _settings() -> Settings:
    return Settings(
        environment="test",
        jwt_secret="test-secret",
        jwt_algorithm="HS256",
        jwt_expires_minutes=30,
    )


def _user(*, password_hash: str | None = None) -> User:
    return User(
        id=uuid4(),
        first_name="Test",
        last_name="User",
        email="test@example.com",
        password_hash=password_hash,
        role=UserRole.COORDINATOR,
    )


def test_register_user_creates_account_when_email_available() -> None:
    # Arrange
    user_repo = MagicMock()
    user_repo.get_by_email.return_value = None
    user_repo.register_user.side_effect = lambda user: user
    service = AuthService(_settings(), user_repo)

    # Act
    result = service.register_user(
        email="new@example.com",
        password="Strong@Pass1",
        first_name="New",
        last_name="User",
        phone="555-0100",
    )

    # Assert
    assert result.email == "new@example.com"
    assert result.password_hash is not None
    assert result.password_hash != "Strong@Pass1"
    user_repo.register_user.assert_called_once()


def test_register_user_raises_when_email_exists() -> None:
    # Arrange
    user_repo = MagicMock()
    user_repo.get_by_email.return_value = _user(password_hash="hashed")
    service = AuthService(_settings(), user_repo)

    # Act / Assert
    with pytest.raises(AuthenticationException, match="Account already exists."):
        service.register_user(
            email="existing@example.com",
            password="Strong@Pass1",
            first_name="Existing",
            last_name="User",
        )


def test_hash_password_raises_for_weak_password() -> None:
    # Arrange
    service = AuthService(_settings(), MagicMock())

    # Act / Assert
    with pytest.raises(WeakPasswordException, match="Password must contain"):
        service.hash_password("weak")


def test_hash_password_raises_when_missing_lowercase_character() -> None:
    # Arrange
    service = AuthService(_settings(), MagicMock())

    # Act / Assert
    with pytest.raises(WeakPasswordException, match="lowercase"):
        service.hash_password("STRONG@PASS1")


def test_authenticate_user_raises_when_email_missing() -> None:
    # Arrange
    user_repo = MagicMock()
    user_repo.get_by_email.return_value = None
    service = AuthService(_settings(), user_repo)

    # Act / Assert
    with pytest.raises(AuthenticationException, match="Incorrect email or password."):
        service.authenticate_user(user_email="missing@example.com", user_password="X")


def test_authenticate_user_raises_when_password_missing() -> None:
    # Arrange
    user_repo = MagicMock()
    user_repo.get_by_email.return_value = _user(password_hash=None)
    service = AuthService(_settings(), user_repo)

    # Act / Assert
    with pytest.raises(AuthenticationException, match="Incorrect email or password."):
        service.authenticate_user(user_email="test@example.com", user_password="X")


def test_authenticate_user_raises_when_password_wrong() -> None:
    # Arrange
    bootstrap_service = AuthService(_settings(), MagicMock())
    user = _user(password_hash=bootstrap_service.hash_password("Strong@Pass1"))
    user_repo = MagicMock()
    user_repo.get_by_email.return_value = user
    service = AuthService(_settings(), user_repo)

    # Act / Assert
    with pytest.raises(AuthenticationException, match="Incorrect email or password."):
        service.authenticate_user(
            user_email="test@example.com", user_password="Wrong@Pass1"
        )


def test_authenticate_user_returns_user_on_valid_password() -> None:
    # Arrange
    user_repo = MagicMock()
    service = AuthService(_settings(), user_repo)
    user = _user(password_hash=service.hash_password("Strong@Pass1"))
    user_repo.get_by_email.return_value = user

    # Act
    result = service.authenticate_user(
        user_email="test@example.com",
        user_password="Strong@Pass1",
    )

    # Assert
    assert result is user


def test_change_password_raises_when_account_has_no_password() -> None:
    # Arrange
    service = AuthService(_settings(), MagicMock())
    user = _user(password_hash=None)

    # Act / Assert
    with pytest.raises(
        AuthenticationException,
        match="This account has no password set yet.",
    ):
        service.change_password(
            user,
            current_password="Strong@Pass1",
            new_password="NewStrong@Pass1",
        )


def test_change_password_raises_when_current_password_is_wrong() -> None:
    # Arrange
    service = AuthService(_settings(), MagicMock())
    user = _user(password_hash=service.hash_password("Strong@Pass1"))

    # Act / Assert
    with pytest.raises(AuthenticationException, match="Current password is incorrect."):
        service.change_password(
            user,
            current_password="Wrong@Pass1",
            new_password="NewStrong@Pass1",
        )


def test_change_password_updates_password_hash() -> None:
    # Arrange
    user_repo = MagicMock()
    user_repo.update.side_effect = lambda user: user
    service = AuthService(_settings(), user_repo)
    user = _user(password_hash=service.hash_password("Strong@Pass1"))

    # Act
    result = service.change_password(
        user,
        current_password="Strong@Pass1",
        new_password="NewStrong@Pass1",
    )

    # Assert
    assert result is user
    assert service._verify_password("NewStrong@Pass1", user.password_hash or "")
    user_repo.update.assert_called_once_with(user)


def test_set_password_updates_password_hash() -> None:
    # Arrange
    user_repo = MagicMock()
    user_repo.update.side_effect = lambda user: user
    service = AuthService(_settings(), user_repo)
    user = _user(password_hash=None)

    # Act
    result = service.set_password(user, new_password="SetStrong@Pass1")

    # Assert
    assert result is user
    assert service._verify_password("SetStrong@Pass1", user.password_hash or "")
    user_repo.update.assert_called_once_with(user)


def test_create_access_token_encodes_expected_claims() -> None:
    # Arrange
    service = AuthService(_settings(), MagicMock())
    user = _user(password_hash="hashed")

    # Act
    token = service.create_access_token(user)
    payload = jwt.decode(
        token,
        service._settings.jwt_secret,
        algorithms=[service._settings.jwt_algorithm],
    )

    # Assert
    assert payload["sub"] == str(user.id)
    assert payload["role"] == user.role
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    assert exp > datetime.now(timezone.utc)


def test_verify_jwt_delegates_to_auth_module() -> None:
    # Arrange
    service = AuthService(_settings(), MagicMock())
    expected_user_id = uuid4()

    # Act
    with patch(
        "trianglebahaiinstitute.auth.verify_jwt", return_value=expected_user_id
    ) as verify_mock:
        result = service.verify_jwt("token")

    # Assert
    assert result == expected_user_id
    verify_mock.assert_called_once_with("token", service._settings)


def test_get_user_by_id_delegates_to_repository() -> None:
    # Arrange
    expected_user_id: UUID = uuid4()
    user = _user(password_hash="hashed")
    user_repo = MagicMock()
    user_repo.get_by_id.return_value = user
    service = AuthService(_settings(), user_repo)

    # Act
    result = service.get_user_by_id(expected_user_id)

    # Assert
    assert result is user
    user_repo.get_by_id.assert_called_once_with(expected_user_id)
