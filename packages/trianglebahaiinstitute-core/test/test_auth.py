# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Tests for the verify_jwt function."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest

from trianglebahaiinstitute.auth import verify_jwt
from trianglebahaiinstitute.config import Settings
from trianglebahaiinstitute.services.auth_service import AuthenticationException

_SETTINGS = Settings(
    jwt_secret="really-secure-secret-is-really-secure",
    jwt_algorithm="HS256",
)


def _encode(payload: dict) -> str:
    return jwt.encode(payload, _SETTINGS.jwt_secret, algorithm=_SETTINGS.jwt_algorithm)


def test_returns_id_for_valid_token() -> None:
    user_id = uuid4()
    token = _encode({"sub": str(user_id)})

    assert verify_jwt(token, _SETTINGS) == user_id


def test_raises_on_invalid_token() -> None:
    with pytest.raises(AuthenticationException):
        verify_jwt("not-a-token", _SETTINGS)


def test_raises_on_expired_token() -> None:
    token = _encode(
        {
            "sub": str(uuid4()),
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        }
    )

    with pytest.raises(AuthenticationException):
        verify_jwt(token, _SETTINGS)


def test_raises_when_sub_claim_missing() -> None:
    token = _encode({})

    with pytest.raises(AuthenticationException):
        verify_jwt(token, _SETTINGS)
