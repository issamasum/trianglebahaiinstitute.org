# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Dependency factories shared accross FastAPI route haddlers."""

from __future__ import annotations

from typing import Annotated, TypeAlias

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from trianglebahaiinstitute.config import Settings, get_settings
from trianglebahaiinstitute.db import get_session
from trianglebahaiinstitute.repositories.user_repository import UserRepository
from trianglebahaiinstitute.services.auth_service import (
    AuthenticationException,
    AuthService,
)
from trianglebahaiinstitute.mytbi.checkin_at_tbi.repository import (
    EventRepository,
    CheckInRepository,
)
from trianglebahaiinstitute.mytbi.checkin_at_tbi.service import (
    EventService,
    CheckInService,
)
from trianglebahaiinstitute.tables.user import User, UserRole
from sqlmodel import Session

__all__ = [
    "AuthServiceDI",
    "SessionDI",
    "SettingsDI",
    "UserRepositoryDI",
    "AuthenticatedUserDI",
    "CoordinatorUserDI",
    "EventRepositoryDI",
    "CheckInRepositoryDI",
    "EventServiceDI",
    "CheckInServiceDI",
    "auth_service_factory",
    "settings_factory",
    "user_repository_factory",
    "get_authenticated_user",
    "require_coordinator",
    "event_repository_factory",
    "check_in_repository_factory",
    "event_service_factory",
    "check_in_service_factory",
]


def auth_service_factory(
    settings: SettingsDI, user_repository: UserRepositoryDI
) -> AuthService:
    """Creates the authentication service for the current request.

    Args:
        settings: Appication settings.
        user_repository: Repository used to load and persist users.

    Returns:
        A configured authenticated service.
    """

    return AuthService(settings, user_repository)


AuthServiceDI: TypeAlias = Annotated[AuthService, Depends(auth_service_factory)]


SessionDI: TypeAlias = Annotated[Session, Depends(get_session)]


def settings_factory() -> Settings:
    """Builds a settings object for FastAPI dependency injection."""
    return get_settings()


SettingsDI: TypeAlias = Annotated[Settings, Depends(settings_factory)]


def user_repository_factory(session: SessionDI) -> UserRepository:
    """Constructs a user repository bound to the current request session."""
    return UserRepository(session)


UserRepositoryDI: TypeAlias = Annotated[
    UserRepository, Depends(user_repository_factory)
]


def get_authenticated_user(
    auth_svc: AuthServiceDI,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
) -> User:
    """Authenticates the current request from a bearer token.

    Args:
        auth_svc: Service used to validate and resolve subject identity.
        credentials: Bearer credentials extracted by FastAPI's HTTPBearer.
    """
    try:
        user_id = auth_svc.verify_jwt(credentials.credentials)
    except AuthenticationException:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    subject = auth_svc.get_user_by_id(user_id)
    if subject is None:
        raise HTTPException(status_code=401, detail="User not found.")
    return subject


AuthenticatedUserDI: TypeAlias = Annotated[User, Depends(get_authenticated_user)]


def require_coordinator(user: AuthenticatedUserDI) -> User:
    """Ensures the authenticated user holds the coordinator role.

    Args:
        user: The currently authenticated user.

    Returns:
        The authenticated user, if they are a coordinator.

    Raises:
        HTTPException: If the user is not a coordinator.
    """
    if user.role != UserRole.COORDINATOR:
        raise HTTPException(status_code=403, detail="Coordinator access required.")
    return user


CoordinatorUserDI: TypeAlias = Annotated[User, Depends(require_coordinator)]


def event_repository_factory(session: SessionDI) -> EventRepository:
    """Constructs an event repository bound to the current request session."""
    return EventRepository(session)


EventRepositoryDI: TypeAlias = Annotated[
    EventRepository, Depends(event_repository_factory)
]


def check_in_repository_factory(session: SessionDI) -> CheckInRepository:
    """Constructs a check-in repository bound to the current request session."""
    return CheckInRepository(session)


CheckInRepositoryDI: TypeAlias = Annotated[
    CheckInRepository, Depends(check_in_repository_factory)
]


def event_service_factory(event_repo: EventRepositoryDI) -> EventService:
    """Creates the event service for the current request."""
    return EventService(event_repo)


EventServiceDI: TypeAlias = Annotated[EventService, Depends(event_service_factory)]


def check_in_service_factory(
    check_in_repo: CheckInRepositoryDI, event_repo: EventRepositoryDI
) -> CheckInService:
    """Creates the check-in service for the current request."""
    return CheckInService(check_in_repo, event_repo)


CheckInServiceDI: TypeAlias = Annotated[
    CheckInService, Depends(check_in_service_factory)
]
