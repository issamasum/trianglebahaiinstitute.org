# Copyright (c) 2026 Issa Masumvbuko
# SPDX-License-Identifier: MIT

from __future__ import annotations

import pytest
from sqlmodel import Session

from trianglebahaiinstitute.repositories.user_repository import UserRepository
from trianglebahaiinstitute.tables.user import User

# -- get_by_email ---

@pytest.mark.integration
def test_get_by_email_returns_none_when_no_user_exists(session: Session) -> None:
    #Arrange
    repo = UserRepository(session)

    # Act
    result = repo.get_by_email("noone@gmail.com")

    # Assert
    assert result is None

@pytest.mark.integration
def test_get_by_email_returns_user_when_exists(session: Session) -> None:
    # Arrange
    repo = UserRepository(session)
    user: User = User(
           first_name="Test",
           last_name="User",
           phone="919-123-1234",
           email="testuser@example.com"
        )
    session.add(user)
    session.flush()

    # Act
    result = repo.get_by_email("testuser@example.com")

    # Assert
    assert result is not None
    assert result.id == user.id
    assert result.email == "testuser@example.com"

# --- register_user ----

@pytest.mark.integration
def test_register_user_persists_and_returns_user(session: Session) -> None:
    # Arrange
    repo = UserRepository(session)
    user: User = User(
               first_name="New",
               last_name="User",
               phone="919-132-1234",
               email="newuser@example.com"
    )

 
    # Act
    result = repo.register_user(user)
 
    # Assert
    assert result.id is not None
    assert result.email == "newuser@example.com"
    persisted = repo.get_by_id(result.id)
    assert persisted is not None
    assert persisted.email == "newuser@example.com"

# --- list_all ----

@pytest.mark.integration
def test_list_all_returns_empty_when_no_users(session: Session) -> None:
    #Arrange
    repo = UserRepository(session)

    # Act
    result = repo.list_all()

    # Assert
    assert result == []


@pytest.mark.integration
def test_list_returns_all_users(session: Session) -> None:
   # Arrange
    repo = UserRepository(session)
    session.add(User(
            first_name="Other",
            last_name="Person",
            phone="919-167-6767",
            email="otherperson@example.com",
        ))
    session.add(User(
            first_name="Other",
            last_name="User",
            phone="919-111-6776",
            email="otheruser@example.com",
        ))
    session.flush()
 
    # Act
    result = repo.list_all()
 
    # Assert
    assert len(result) == 2
    emails = {user.email for user in result}
    assert emails == {"otherperson@example.com", "otheruser@example.com"}

# ---update ----

@pytest.mark.integration
def test_update_user_persists_changes(session: Session) -> None:
   # Arrange
    repo = UserRepository(session)
    user = User(
            first_name="Test",
            last_name="User",
            phone="919-123-1234",
            email="testuser@example.com",
    )
    session.add(user)
    session.flush()
    
    # Act
    user.first_name = "New"
    result = repo.update_user(user)
 
    # Assert
    assert result.first_name == "New"
    persisted = repo.get_by_email("testuser@example.com")
    assert persisted is not None
    assert persisted.first_name == "New"
