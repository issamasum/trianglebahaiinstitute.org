# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Route exports for the FastAPI application."""

from api.routes.check_in_at_tbi import (
    admin_general_router as check_in_admin_general_router,
    admin_router as check_in_admin_router,
    router as check_in_router,
)
from api.routes.auth import router as authentication_router
from api.routes.health import router as health_router
from api.routes.me import router as auth_user_router

API_ROUTERS = [
    health_router,
    check_in_admin_general_router,
    check_in_admin_router,
    check_in_router,
    authentication_router,
    auth_user_router,
]

__all__ = ["API_ROUTERS"]
