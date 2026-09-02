# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Models for authontication-facing APIs."""

from datetime import datetime
from typing import Optional
from uuid import UUID


from trianglebahaiinstitute.tables.user import UserRole

from pydantic import BaseModel, EmailStr


class UserSignUpRequest(BaseModel):
    """Payload for signing up into myTBI."""

    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None


class UserLoginRequest(BaseModel):
    """Payload for logging into myTBI."""

    email: EmailStr
    password: str


class UserProfile(BaseModel):
    """Represents the authonticated user profile."""

    model_config = {"from_attributes": True}

    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    role: Optional[UserRole] = None
    phone: Optional[str] = None
    last_logged_at: Optional[datetime] = None


class UpdateProfileRequest(BaseModel):
    """Payload for updating the authenticated user profile."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class TokenResponse(BaseModel):
    """Access token issued after succesful login or sign up."""

    access_token: str
    token_type: str = "bearer"
