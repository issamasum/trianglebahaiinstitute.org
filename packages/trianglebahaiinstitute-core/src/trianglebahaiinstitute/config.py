# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Application configuration models and helpers."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, computed_field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url

Environment = Literal["development", "test", "production"]

ENV_FILE_NAME = ".env"
DEFAULT_JWT_SECRET = "reallysecuresecret-dev-default-key"
_DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://postgres:postgres@postgres:5432/trianglebahaiinstitute"
)
_DEFAULT_TEST_DATABASE_URL = _DEFAULT_DATABASE_URL + "_test"


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
    test_database_url: str | None = None
    db_echo: bool = False

    # App / API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    # Auth
    host: str = "localhost:4200"
    jwt_secret: str = Field(
        default=DEFAULT_JWT_SECRET,
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
        """Returns the database URL to use for the current environment.

        In test, ``TEST_DATABASE_URL`` is preferred. ``DATABASE_URL`` is only
        honoured if its database name ends in ``_test``, so a test run
        can never target the development database.
        """
        if self.is_test:
            if self.test_database_url:
                return self.test_database_url
            if self.database_url and (
                make_url(self.database_url).database or ""
            ).endswith("_test"):
                return self.database_url
            return _DEFAULT_TEST_DATABASE_URL

        if self.database_url:
            return self.database_url

        return _DEFAULT_DATABASE_URL

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

    @field_validator("database_url", "test_database_url")
    @classmethod
    def _use_psycopg_driver(cls, value: str | None) -> str | None:
        """Ensures that PostgreSQL URLs use the psycopg driver."""
        if value is None:
            return None
        for prefix in ("postgres://", "postgresql://"):
            if value.startswith(prefix):
                return "postgresql+psycopg://" + value[len(prefix) :]
        return value

    @model_validator(mode="after")
    def _require_production_settings(self) -> Settings:
        """Falis fast if production is missing required secrets."""
        if self.is_production:
            problems = []
            if not self.database_url:
                problems.append("DATABASE_URL must be set in production.")
            if self.jwt_secret == DEFAULT_JWT_SECRET:
                problems.append(
                    "JWT_SECRET must be overridden in production (currently using default)."
                )
            if problems:
                raise ValueError("; ".join(problems))
        return self


@lru_cache
def get_settings() -> Settings:
    """Returns a cached settings instance for the current process."""
    return Settings()
