# Copyright (c) Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Authentication routes for the public API."""

from fastapi import APIRouter, HTTPException


from trianglebahaiinstitute.services.auth_service import (
    AuthenticationException,
    WeakPasswordException,
)
from ..di import AuthServiceDI

from ..models import UserSignUpRequest, UserLoginRequest, TokenResponse

router = APIRouter(prefix="/mytbi/auth", tags=["Authentication"])


@router.post(
    "/signup",
    summary="Starts sign up process",
)
def user_signup(payload: UserSignUpRequest, auth_svc: AuthServiceDI) -> TokenResponse:
    """Registers a new user and returns an access token.

    Args:
        payload: The new user's registration details.
        auth_svc: Service used to coordinate authentication.

    Returns:
        An access token for the newly created user.

    Raises:
        HTTPException: If the email is already registered, or
        if the password does not meet strength requirements.
    """
    try:
        user = auth_svc.register_user(
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name,
            last_name=payload.last_name,
            phone=payload.phone,
        )
    except AuthenticationException:
        raise HTTPException(status_code=409, detail="Email already exists.")
    except WeakPasswordException:
        raise HTTPException(status_code=400, detail="Weak password")

    token = auth_svc.create_access_token(user)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def user_login_authentication(
    payload: UserLoginRequest, auth_svc: AuthServiceDI
) -> TokenResponse:
    """Authenticates a user and returns an access token.

    Args:
        payload: The user's login credentials.
        auth_svc: Service used to coordinate authentication.

    Returns:
        An access token for the authenticated user.

    Raises:
        HTTPException: If the email or password is incorrect.
    """
    try:
        user = auth_svc.authenticate_user(
            user_email=payload.email, user_password=payload.password
        )
    except AuthenticationException:
        raise HTTPException(status_code=401, detail="You are not authenticated.")

    token = auth_svc.create_access_token(user)
    return TokenResponse(access_token=token)
