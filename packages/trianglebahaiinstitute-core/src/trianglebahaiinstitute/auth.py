# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

"""JWT verification."""

from uuid import UUID

import jwt

from .config import Settings
from .services.auth_service import AuthenticationException


def verify_jwt(token: str, settings: Settings) -> int:
    """Decodes a JWT and returns the user's ID.

    Args:
        token: Encoded JWT issed by AuthService.
        settings: Application settings containing the JWT secret and algorithim.
    """

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise AuthenticationException() from exc
