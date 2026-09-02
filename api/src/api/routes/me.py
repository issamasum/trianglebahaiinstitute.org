# Copyright (c) Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Authenticated user profile routes."""

from typing import Annotated

from fastapi import APIRouter, Body, HTTPException

from ..di import AuthenticatedUserDI, UserRepositoryDI
from ..models import UpdateProfileRequest, UserProfile

router = APIRouter(prefix="/mytbi/me", tags=["Authenticated User"])


@router.get(
    "",
    response_model=UserProfile,
    summary="Get the authenticated user profile",
    response_description="Profile details for the authenticated user.",
    responses={401: {"description": "Bearer token is missing, invalid, or expired."}},
)
def get_current_subject_profile(subject: AuthenticatedUserDI) -> UserProfile:
    """Returns the authenticated user's profile.

    Args:
        subject: Authenticated subject resolved from the bearer token.

    Returns:
        A UserProfile for the API.
    """
    return UserProfile.model_validate(subject.model_dump(mode="json"))


@router.patch(
    "",
    response_model=UserProfile,
    summary="Update the authenticated user's profile",
    response_description="The updated profile.",
    responses={
        401: {"description": "Bearer token is missing, invalid, or expired."},
        409: {"description": "The requested email is already in use."},
    },
)
def update_current_subject_profile(
    subject: AuthenticatedUserDI,
    body: Annotated[UpdateProfileRequest, Body()],
    user_repo: UserRepositoryDI,
) -> UserProfile:
    """Updates whichever fields are provided on the authenticated user's profile.

    Fields omitted from the request body are left unchanged.

    Args:
        subject: TAuthenticated subject resolved from the bearer token.
        body: Profile update payload.
        user_repo: Repository used to persist the change.

    Returns:
        The updated user profile.

    Raises:
        HTTPException: If the requested email is already taken by another user.
    """
    updates = body.model_dump(exclude_unset=True)

    if "email" in updates and updates["email"] != subject.email:
        existing = user_repo.get_by_email(updates["email"])
        if existing is not None and existing.id != subject.id:
            raise HTTPException(status_code=409, detail="Email already in use.")

    for field, value in updates.items():
        setattr(subject, field, value)

    updated = user_repo.update_user(subject)
    return UserProfile.model_validate(updated.model_dump(mode="json"))
