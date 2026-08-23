# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Route exports for the FastAPI application."""

from api.routes.checkin_at_tbi import (
    admin_router as check_in_admin_router,
    admin_general_router as check_in_admin_general_router,
    router as check_in_router
)

API_ROUTERS = [
    check_in_admin_general_router,
    check_in_admin_router,
    check_in_router,
]

__all__ = ["API_ROUTERS"]