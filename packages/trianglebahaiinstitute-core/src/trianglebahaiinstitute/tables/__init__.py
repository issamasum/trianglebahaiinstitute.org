# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Imports all SQLModel table modules so metadata registration is explicit."""

from ..mytbi.checkin_at_tbi.tables import (
    CheckIn,
    Event,
)
from .user import User, UserRole

__all__ = [
    "Event",
    "CheckIn",
    "User",
    "UserRole",
]
