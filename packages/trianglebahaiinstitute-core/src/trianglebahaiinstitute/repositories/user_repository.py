# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Persistence helper for user records."""

from uuid import UUID

from pydantic import EmailStr
from sqlmodel import select

from ..tables.user import User
from .base_repository import BaseRepository


class UserRepository(BaseRepository[User, UUID]):
    """Provides user lookup and persistence operations."""

    @property
    def model_type(self) -> type[User]:
        """Returns the SQLModel class managed by this repository."""
        return User

    def list_all(self) -> list[User]:
        """Returns all registerred users.

        Returns:
            A list of all user records.
        """
        return list(self._session.exec(select(User)).all())

    def register_user(self, new_user: User) -> User:
        """Persist a new user record and reloads database defaults.

        Args:
            new_user: User instance to add

        Returns:
            The persisted user with refreshed database state.
        """
        return self.create(new_user)

    def update_user(self, user: User) -> User:
        """Persist changes to an existing user and refreshes database state.

        Args:
            user: User instance with updated fields.

        Returns:
            The updated user with refreshed database state.
        """
        return self.update(user)

    def get_by_email(self, email: EmailStr) -> User | None:
        """Looks up a user by their email"""

        return self._session.exec(select(User).where(User.email == email)).first()
