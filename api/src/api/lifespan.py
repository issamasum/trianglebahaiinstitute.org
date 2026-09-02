"""Startup and shutdown wiring for the FastAPI application."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from trianglebahaiinstitute.db import get_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Runs startup and shutdown logic around the application's lifetime.

    On startup, verifies the database is reachable so a misconfigured
    connection fails fast at boot instead of on the first request.
    On shutdown, disposes the engine's connection pool cleanly.

    Args:
        app: The FastAPI application instance.

    Yields:
        Control back to FastAPI while the application is running.
    """
    engine = get_engine()
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    yield

    engine.dispose()
