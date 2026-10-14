# Copyright (c) 2026 Kris Jordan
# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from trianglebahaiinstitute.config import (
    DEFAULT_JWT_SECRET,
    ENV_FILE_NAME,
    Settings,
    find_env_file,
    get_settings,
)


@pytest.fixture
def clean_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Isolates Settings from real .env file and environment variables."""
    monkeypatch.chdir(tmp_path)
    for name in ("ENVIRONMENT", "DATABASE_URL", "JWT_SECRET"):
        monkeypatch.delenv(name, raising=False)


def build_settings(**overrides: Any) -> Settings:
    settings_data = {
        "app_name": "trianglebahaiinstitute",
        "environment": "development",
        "database_url": None,
        "db_echo": False,
        "api_host": "0.0.0.0",
        "api_port": 8000,
        "log_level": "INFO",
    }
    settings_data.update(overrides)
    return Settings.model_construct(**settings_data)


def test_effective_database_url_uses_explicit_database_url() -> None:
    # Arrange
    settings = build_settings(database_url="sqlite:///explicit.db")

    # Act
    database_url = settings.effective_database_url

    # Assert
    assert database_url == "sqlite:///explicit.db"


def test_effective_database_url_uses_test_default_for_test_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = build_settings(environment="test")

    # Act
    database_url = settings.effective_database_url

    # Assert
    assert database_url.endswith("/trianglebahaiinstitute_test")


def test_effective_database_url_uses_default_for_non_test_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = build_settings(environment="development")

    # Act
    database_url = settings.effective_database_url

    # Assert
    assert database_url.endswith("/trianglebahaiinstitute")


def test_environment_flags_reflect_current_environment() -> None:
    # Arrange
    development_settings = build_settings(environment="development")
    test_settings = build_settings(environment="test")
    production_settings = build_settings(environment="production")

    # Act
    development_flags = (
        development_settings.is_development,
        development_settings.is_test,
        development_settings.is_production,
    )
    test_flags = (
        test_settings.is_development,
        test_settings.is_test,
        test_settings.is_production,
    )
    production_flags = (
        production_settings.is_development,
        production_settings.is_test,
        production_settings.is_production,
    )

    # Assert
    assert development_flags == (True, False, False)
    assert test_flags == (False, True, False)
    assert production_flags == (False, False, True)


def test_get_settings_returns_cached_settings_instance() -> None:
    # Arrange
    get_settings.cache_clear()

    # Act
    first_settings = get_settings()
    second_settings = get_settings()

    # Assert
    assert first_settings is second_settings


def test_find_env_file_returns_nearest_parent_env_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Arrange
    repo_dir = tmp_path / "repo"
    nested_dir = repo_dir / "packages" / "trianglebahaiinstitute-core"
    nested_dir.mkdir(parents=True)
    env_file = repo_dir / ENV_FILE_NAME
    env_file.write_text("LOG_LEVEL=DEBUG\n", encoding="utf-8")
    monkeypatch.chdir(nested_dir)

    # Act
    discovered_env_file = find_env_file()

    # Assert
    assert discovered_env_file == env_file


def test_settings_load_from_nearest_parent_env_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Arrange
    repo_dir = tmp_path / "repo"
    nested_dir = repo_dir / "packages" / "trianglebahaiinstitute-core"
    nested_dir.mkdir(parents=True)
    env_file = repo_dir / ENV_FILE_NAME
    env_file.write_text("LOG_LEVEL=DEBUG\n", encoding="utf-8")
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.chdir(nested_dir)

    # Act
    settings = Settings()

    # Assert
    assert settings.log_level == "DEBUG"


def test_settings_require_env_file_in_development(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Arrange
    working_dir = tmp_path / "repo" / "packages" / "trianglebahaiinstitute-core"
    working_dir.mkdir(parents=True)
    monkeypatch.chdir(working_dir)
    monkeypatch.setenv("ENVIRONMENT", "development")

    # Act / Assert
    with pytest.raises(FileNotFoundError, match="Copy .env.example to .env"):
        Settings()


def test_settings_allow_missing_env_file_outside_development(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Arrange
    working_dir = tmp_path / "repo" / "packages" / "trianglebahaiinstitute-core"
    working_dir.mkdir(parents=True)
    monkeypatch.chdir(working_dir)

    # Act
    settings = Settings(environment="test")

    # Assert
    assert settings.environment == "test"


def test_production_requires_database_url(clean_env: None) -> None:
    # Act / Assert
    with pytest.raises(ValidationError, match="DATABASE_URL must be set"):
        Settings(environment="production", jwt_secret="x" * 32)


def test_production_rejects_default_jwt_secret(clean_env: None) -> None:
    # Act / Assert
    with pytest.raises(ValidationError, match="JWT_SECRET must be overridden"):
        Settings(environment="production", database_url="postgresql://u:p@h/db")


def test_production_accepts_explicit_required_settings(clean_env: None) -> None:
    # Act
    settings = Settings(
        environment="production",
        database_url="postgresql://u:p@h/db",
        jwt_secret="x" * 32,
    )

    # Assert
    assert settings.is_production


@pytest.mark.parametrize(
    "raw_url",
    ["postgres://u:p@h:5432/db", "postgresql://u:p@h:5432/db"],
)
def test_database_url_is_rewritten_to_psycopg_driver(
    clean_env: None, raw_url: str
) -> None:
    # Act
    settings = Settings(environment="test", database_url=raw_url)

    # Assert
    assert settings.database_url == "postgresql+psycopg://u:p@h:5432/db"


def test_database_url_with_explicit_driver_is_unchanged(clean_env: None) -> None:
    # Arrange
    url = "postgresql+psycopg://u:p@h:5432/db"

    # Act
    settings = Settings(environment="test", database_url=url)

    # Assert
    assert settings.database_url == url


def test_development_and_test_allow_default_secrets(clean_env: None) -> None:
    # Act
    settings = Settings(environment="test")

    # Assert
    assert settings.jwt_secret == DEFAULT_JWT_SECRET
