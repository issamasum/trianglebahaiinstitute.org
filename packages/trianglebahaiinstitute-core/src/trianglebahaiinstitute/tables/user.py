# Copyright (c) 2026 Issa Masumbuko
# SPDX-LIcence-Identifier: MIT

"""Database-backed user models"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Uuid, func
from sqlmodel import Enum, Field, SQLModel


class UserRole(str, enum.Enum):
    """Role a use holds when accessing role-based features."""

    COORDINATOR = "coordinator"


class User(SQLModel, table=True):
    """Represents an authenticated user using featured requiring authentication."""

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(Uuid, primary_key=True)
    )
    first_name: str = Field(
        nullable=False
    )
    last_name: str = Field(
        nullable=False
    )
    phone: str = Field(
        nullable=True
    )
    email: str = Field(
        nullable=False, unique=True
    )
    password_hash: str = Field(
       nullable=True 
    )
    role: UserRole = Field(
        sa_column=Column(
            Enum(
                UserRole,
                values_callable=lambda e: [m.value for m in e]),
                nullable=True,
            )
    )
    is_active: bool = Field(
        default=True,
        nullable=False
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        default=None
    )
    last_logged_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
        ),
        default=None,
    )
