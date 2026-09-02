# Copyright (c) 2026 Kris Jordan
# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Application configuration models and helpers."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "test", "production"]

ENV_FILE_NAME = ".env"


def find_env_file(start_dir: Path | None = None) -> Path | None:
    """Searches the current directory and its parents for a `.env` file.

    Args:
        start_dir: Directory to start searching from. Defaults to the current
            working directory.

    Returns:
        The first `.env` file found while walking upward, or `None` if no file
        exists.
    """
    current_dir = (start_dir or Path.cwd()).resolve()

    for directory in (current_dir, *current_dir.parents):
        candidate = directory / ENV_FILE_NAME
        if candidate.is_file():
            return candidate

    return None


class Settings(BaseSettings):
    """Defines environment-backed settings used throughout the workspace."""

    app_name: str = "trianglebahaiinstitute"
    environment: Environment = "development"

    # Database
    database_url: str | None = None
    db_echo: bool = True

    # App / API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    # Auth
    host: str = "localhost:4200"
    jwt_secret: str = Field(
        default="reallysecuresecret-dev-default-key",
        description="Must be overridden via env vari in production.",
    )
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 720

    # Static files
    static_dir: str = ""

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    def __init__(self, **values: Any) -> None:
        """Builds settings using the nearest `.env` file when present.

        In development mode, a missing `.env` is treated as a setup error.
        In test and production, environment variables alone are allowed.
        """
        environment = str(
            values.get("environment") or os.environ.get("ENVIRONMENT") or "development"
        ).lower()
        env_file = find_env_file()

        if env_file is None and environment == "development":
            raise FileNotFoundError(
                "No .env file found in the current working directory or any parent directory. "
                "Copy .env.example to .env in root of repo before running in development."
            )

        super().__init__(_env_file=env_file, **values)

    @computed_field
    @property
    def effective_database_url(self) -> str:
        """Returns the configured database URL or the default for the environment."""
        if self.database_url:
            return self.database_url

        if self.environment == "test":
            return "postgresql+psycopg://postgres:postgres@postgres:5432/trianglebahaiinstitute_test"

        return "postgresql+psycopg://postgres:postgres@postgres:5432/trianglebahaiinstitute"

    @computed_field
    @property
    def is_development(self) -> bool:
        """Reports whether the current environment is development."""
        return self.environment == "development"

    @computed_field
    @property
    def is_test(self) -> bool:
        """Reports whether the current environment is test."""
        return self.environment == "test"

    @computed_field
    @property
    def is_production(self) -> bool:
        """Reports whether the current environment is production."""
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Returns a cached settings instance for the current process."""
    return Settings()
