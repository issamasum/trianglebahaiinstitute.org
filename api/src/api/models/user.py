# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Models for authontication-facing APIs."""

from datetime import datetime
from typing import Optional

from trianglebahaiinstitute.tables.user import UserRole

from pydantic import BaseModel, EmailStr



class UserSignUp(BaseModel):
    """Payload for signing up into myTBI."""

    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None


class UserLogin(BaseModel):
    """Payload for logging into myTBI."""

    email: EmailStr
    password: str


class UserProfile(BaseModel):
    """Represents the authonticated user profile."""

    id: int
    first_name: str
    last_name: str
    email: EmailStr
    role: Optional[UserRole] = None
    phone: Optional[str] = None
    last_logged_at: Optional[datetime]
    
