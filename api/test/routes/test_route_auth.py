from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from trianglebahaiinstitute.services.auth_service import (
    AuthenticationException,
    WeakPasswordException,
)
from trianglebahaiinstitute.tables.user import User, UserRole

from api.di import auth_service_factory
from api.main import app
from api.routes.auth import user_login_authentication, user_signup


def _stub_user() -> User:
    """Creates a stub user suitable for route-level testing."""
    return User(
        id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        first_name="Test",
        last_name="User",
        email="test@example.com",
        phone=None,
        password_hash="hashed",
        role=UserRole.COORDINATOR,
        is_active=True,
    )


# Unit tests


def test_user_signup_returns_access_token() -> None:
    # Arrange
    auth_svc = MagicMock()
    auth_svc.register_user.return_value = _stub_user()
    auth_svc.create_access_token.return_value = "signup-token"
    payload = MagicMock(
        email="newuser@example.com",
        password="Strong@Pass1",
        first_name="New",
        last_name="User",
        phone="555-0100",
    )

    # Act
    response = user_signup(payload, auth_svc)

    # Assert
    assert response.access_token == "signup-token"
    assert response.token_type == "bearer"
    auth_svc.register_user.assert_called_once_with(
        email="newuser@example.com",
        password="Strong@Pass1",
        first_name="New",
        last_name="User",
        phone="555-0100",
    )
    auth_svc.create_access_token.assert_called_once_with(
        auth_svc.register_user.return_value
    )


def test_user_signup_raises_409_when_email_exists() -> None:
    # Arrange
    auth_svc = MagicMock()
    auth_svc.register_user.side_effect = AuthenticationException("exists")
    payload = MagicMock(
        email="existing@example.com",
        password="Strong@Pass1",
        first_name="Existing",
        last_name="User",
        phone=None,
    )

    # Act / Assert
    with pytest.raises(HTTPException) as exc_info:
        user_signup(payload, auth_svc)

    exc = exc_info.value
    assert exc.status_code == 409
    assert exc.detail == "Email already exists."
    auth_svc.create_access_token.assert_not_called()


def test_user_signup_raises_400_when_password_is_weak() -> None:
    # Arrange
    auth_svc = MagicMock()
    auth_svc.register_user.side_effect = WeakPasswordException("weak password")
    payload = MagicMock(
        email="weak@example.com",
        password="weak",
        first_name="Weak",
        last_name="Password",
        phone=None,
    )

    # Act / Assert
    with pytest.raises(HTTPException) as exc_info:
        user_signup(payload, auth_svc)

    exc = exc_info.value
    assert exc.status_code == 400
    assert exc.detail == "Weak password"
    auth_svc.create_access_token.assert_not_called()


def test_user_login_authentication_returns_access_token() -> None:
    # Arrange
    auth_svc = MagicMock()
    auth_svc.authenticate_user.return_value = _stub_user()
    auth_svc.create_access_token.return_value = "login-token"
    payload = MagicMock(email="user@example.com", password="Strong@Pass1")

    # Act
    response = user_login_authentication(payload, auth_svc)

    # Assert
    assert response.access_token == "login-token"
    assert response.token_type == "bearer"
    auth_svc.authenticate_user.assert_called_once_with(
        user_email="user@example.com", user_password="Strong@Pass1"
    )
    auth_svc.create_access_token.assert_called_once_with(
        auth_svc.authenticate_user.return_value
    )


def test_user_login_authentication_raises_401_for_bad_credentials() -> None:
    # Arrange
    auth_svc = MagicMock()
    auth_svc.authenticate_user.side_effect = AuthenticationException("bad credentials")
    payload = MagicMock(email="user@example.com", password="Wrong@Pass1")

    # Act / Assert
    with pytest.raises(HTTPException) as exc_info:
        user_login_authentication(payload, auth_svc)

    exc = exc_info.value
    assert exc.status_code == 401
    assert exc.detail == "You are not authenticated."
    auth_svc.create_access_token.assert_not_called()


# Integration tests


@pytest.mark.integration
def test_signup_endpoint_returns_token(client: TestClient) -> None:
    # Arrange
    auth_svc = MagicMock()
    auth_svc.register_user.return_value = _stub_user()
    auth_svc.create_access_token.return_value = "integration-signup-token"
    app.dependency_overrides[auth_service_factory] = lambda: auth_svc

    # Act
    response = client.post(
        "/api/mytbi/auth/signup",
        json={
            "first_name": "New",
            "last_name": "User",
            "email": "newuser@example.com",
            "password": "Strong@Pass1",
            "phone": "919-123-0000",
        },
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "access_token": "integration-signup-token",
        "token_type": "bearer",
    }


@pytest.mark.integration
def test_signup_endpoint_returns_409_for_existing_email(client: TestClient) -> None:
    # Arrange
    auth_svc = MagicMock()
    auth_svc.register_user.side_effect = AuthenticationException("exists")
    app.dependency_overrides[auth_service_factory] = lambda: auth_svc

    # Act
    response = client.post(
        "/api/mytbi/auth/signup",
        json={
            "first_name": "Existing",
            "last_name": "User",
            "email": "existing@example.com",
            "password": "Strong@Pass1",
            "phone": "919-123-0000",
        },
    )

    # Assert
    assert response.status_code == 409
    assert response.json() == {"detail": "Email already exists."}


@pytest.mark.integration
def test_signup_endpoint_returns_400_for_weak_password(client: TestClient) -> None:
    # Arrange
    auth_svc = MagicMock()
    auth_svc.register_user.side_effect = WeakPasswordException("Weak password")
    app.dependency_overrides[auth_service_factory] = lambda: auth_svc

    # Act
    response = client.post(
        "/api/mytbi/auth/signup",
        json={
            "first_name": "Weak",
            "last_name": "Password",
            "email": "weak@example.com",
            "password": "weak",
            "phone": "555-0100",
        },
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Weak password"}


@pytest.mark.integration
def test_login_endpoint_returns_token(client: TestClient) -> None:
    # Arrange
    auth_svc = MagicMock()
    auth_svc.authenticate_user.return_value = _stub_user()
    auth_svc.create_access_token.return_value = "integration-login-token"
    app.dependency_overrides[auth_service_factory] = lambda: auth_svc

    # Act
    response = client.post(
        "/api/mytbi/auth/login",
        json={"email": "user@example.com", "password": "Strong@Pass1"},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "access_token": "integration-login-token",
        "token_type": "bearer",
    }


@pytest.mark.integration
def test_login_endpoint_returns_401_for_bad_credentials(client: TestClient) -> None:
    # Arrange
    auth_svc = MagicMock()
    auth_svc.authenticate_user.side_effect = AuthenticationException("bad credentials")
    app.dependency_overrides[auth_service_factory] = lambda: auth_svc

    # Act
    response = client.post(
        "/api/mytbi/auth/login",
        json={"email": "user@example.com", "password": "Wrong@Pass1"},
    )

    # Assert
    assert response.status_code == 401
    assert response.json() == {"detail": "You are not authenticated."}
