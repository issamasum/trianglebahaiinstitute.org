# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT


import re
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from pwdlib import PasswordHash
from pydantic import EmailStr

from ..config import Settings
from ..repositories.user_repository import UserRepository
from ..tables.user import User

password_hash = PasswordHash.recommended()

MIN_PASSWORD_LENGTH: int = 8
SPECIAL_CHARACTERS = "!@#$%&"
SPECIAL_CHARACTER_PATTERN = re.compile(f"[{re.escape(SPECIAL_CHARACTERS)}]")

class AuthenticationException(Exception): ...

class WeakPasswordException(Exception): ...

class AuthService:
    """Coordinate authentication."""

    def __init__(self, settings: Settings, user_repo: UserRepository) -> None:
        """Initializes the authentication serivce.

        Args:
            settings: Application settings usef for external serivce configaration.
            user_repo: Repository used to read and persist users.
        
            Returns:
                None
        """
        self._settings = settings
        self._user_repo = user_repo


    # Password auth

    def hash_password(self, user_password: str) -> str:
        """Hasshes a user's password for storage.

        Args:
            user_password: the password provided by the user.

        Returns:
            The hash for this password.
        """

        self._validate_password_strength(user_password)
        return password_hash.hash(user_password)


    def _verify_password(self, user_passowrd: str, hashed: str) -> bool:
        """Verifies a user's password matches its hashed string.

        Args:
            user_password: the password provided by the user.
            hashed: the password's hash string.
        
        Returns:
            Returns True if they match.
        """
        return password_hash.verify(user_passowrd, hashed)
    

    def _validate_password_strength(self, user_password: str) -> None:
        """Validates a user's passowrd for security and validity.
        Args: 
            user_password: the password provided by the user
        
        Returns:
            None
        """

        problems: list[str] = []

        if len(user_password) < MIN_PASSWORD_LENGTH:
            problems.append(f"at least {MIN_PASSWORD_LENGTH} characters")
        if not any(c.isupper() for c in user_password):
            problems.append("at least one uppercase letter")
        if not any(c.islower() for c in user_password):
            problems.append("at least one lowercase letter")
        if not SPECIAL_CHARACTER_PATTERN.search(user_password):
            problems.append(f"at least one special character ({SPECIAL_CHARACTERS})")
 
        if problems:
            raise WeakPasswordException(
                "Password must contain " + ", ".join(problems) + "."
            )


    def register_user(
            self,
            *,
            email: EmailStr,
            password: str,
            first_name: str,
            last_name: str,
            phone: str | None = None,
    ) -> User:
        """Create a new user account
        Args:
            email: The user's email.
            password: user's password. 
            first_name: The user's first name.
            last_name: The user's last name.
            phone: Optional phone number.
 
        Returns:
            The newly created user.
 
        Raises:
            AuthenticationException: If a user with this email already exists.
            WeakPasswordException: If password doesn't meet strength rules.
        """

        existing_user: User | None = self._user_repo.get_by_email(email)

        if existing_user is not None:
            raise AuthenticationException("Account already exists.")

        user: User = User(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            password_hash=self.hash_password(password),    
        )
        return self._user_repo.register_user(user)


    def authenticate_user(self, *, user_email: EmailStr, user_password: str) -> User:
        """Authenticates a user based on their credentials.

        Args: 
            user_email: The email the user has provided.
            user_password: The passowrd the user has provided.

        Returns:
            The matched user.
        
        Raises:
        AuthenticationException: If the email is unknown, the account
            has no password set, or the password is wrong.
        """

        user = self._user_repo.get_by_email(user_email)

        if user is None or user.password_hash is None:
            raise AuthenticationException("Incorrect email or password.")
        if not self._verify_password(user_password, user.password_hash):
            raise AuthenticationException("Incorrect email or password.")
        return user

    def change_password(self, user: User, *, current_password: str, new_password: str) -> User:
        """Changes an existing password.

        Args:
            user: the user requesting the password change
            current_passowrd: The user's current password.
            new_password: The new password.

        Returns:
            Returns the user.
        
        Raises:
            AuthenticationException: If the user's current password is wrong, or the
                account has no password set yet.
            WeakPasswordException: If the new password is too weak.
        """
        if user.password_hash is None:
            raise AuthenticationException(
                "This account has no password set yet."
            )
        if not self._verify_password(current_password, user.password_hash):
            raise AuthenticationException(
                "Current password is incorrect."
            )
        user.password_hash = self.hash_password(new_password)
        return self._user_repo.update(user)

    def set_password(self, user: User, *, new_password: str) -> User:
        """Sets a new password.

        Args: 
            user: The user requesting the service.
            new_password: The user's new password.
        
        Returns:
            The updated user.
 
        Raises:
            WeakPasswordException: If new password is too weak.
        """
        user.password_hash = self.hash_password(new_password)
        return self._user_repo.update(user)

    
    # JWT 

    def create_access_token(self, user: User) -> str:
        """Issues a singed JWT for an authenticated user.
        Args:
            user: the authenticated user to encode into the token subject.

        Returns:
            Encoded JWT string.
        """

        payload = {
            "sub": str(user.id),
            "role": user.role,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=self._settings.jwt_expires_minutes),

        }
        return jwt.encode(
            payload, self._settings.jwt_secret, algorithm=self._settings.jwt_algorithm
        )

    def verify_jwt(self, token: str) -> UUID:
        """ Decodes a JWT and returns the user ID.
        
        Args:
            token: Encoded JWT issused by this service.
        
        Return:
            The user ID stored in the token subject claim.
        
        Raises:
            AuthenticationException: If the token is invalid or expired.
        """
        from ..auth import verify_jwt
        
        return verify_jwt(token, self._settings)

    def get_user_by_id(self, user_id: UUID) -> User | None:
        """Looks up suer by ID

        Args:
            user_id: The user's ID to look up.
        
        Returns:
            The matching user when found; otherwise, ``None``.
        """
        return self._user_repo.get_by_id(user_id)
    