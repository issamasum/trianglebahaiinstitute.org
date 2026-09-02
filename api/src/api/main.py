"""Application entrypoint for FastAI adapter."""

from __future__ import annotations


from fastapi import FastAPI
from trianglebahaiinstitute.config import Settings

from api.lifespan import lifespan
from api.openapi import API_DESCRIPTION, OPENAPI_TAGS, generate_openation_id
from api.routes import API_ROUTERS


def create_app(settings: Settings) -> FastAPI:
    """Creates and cofigures the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        description=API_DESCRIPTION,
        openapi_tags=OPENAPI_TAGS,
        generate_unique_id_function=generate_openation_id,
        lifespan=lifespan,
    )

    for router in API_ROUTERS:
        app.include_router(router, prefix="/api")

    return app


settings = Settings()
app = create_app(settings)
