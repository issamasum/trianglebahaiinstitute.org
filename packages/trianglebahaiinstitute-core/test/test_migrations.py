# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Integration tests that run the real Alembic migrations against PostgreSQL."""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from collections.abc import Iterator
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url

from trianglebahaiinstitute import db
from trianglebahaiinstitute.db import load_table_metadata

TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@postgres:5432/trianglebahaiinstitute_test",
)


@pytest.fixture()
def scratch_database_url() -> Iterator[str]:
    """Creates an empty throwaway database and drops it afterwards."""
    base_url = make_url(TEST_DB_URL)
    name = f"migrations_check_{uuid.uuid4().hex[:8]}"
    admin_engine = create_engine(
        base_url.set(database="postgres"), isolation_level="AUTOCOMMIT"
    )
    try:
        with admin_engine.connect() as conn:
            conn.execute(text(f'CREATE DATABASE "{name}"'))
    except Exception as exc: 
        admin_engine.dispose()
        pytest.skip(f"PostgreSQL unavailable for migration tests: {exc}")

    try:
        yield base_url.set(database=name).render_as_string(hide_password=False)
    finally:
        with admin_engine.connect() as conn:
            conn.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        admin_engine.dispose()


def _alembic_config(url: str) -> Config:
    cfg = Config(str(db._ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    return cfg


def test_run_migrations_creates_schema_matching_models(
    scratch_database_url: str,
) -> None:
    # Arrange
    settings = SimpleNamespace(effective_database_url=scratch_database_url)
    load_table_metadata()

    # Act
    with patch("trianglebahaiinstitute.db.get_settings", return_value=settings):
        db.run_migrations()

    # Assert
    engine = create_engine(scratch_database_url)
    try:
        tables = set(inspect(engine).get_table_names())
    finally:
        engine.dispose()
    assert {"alembic_version", "checkin", "event"} <= tables

    command.check(_alembic_config(scratch_database_url))


def test_run_migrations_is_idempotent(scratch_database_url: str) -> None:
    # Arrange
    settings = SimpleNamespace(effective_database_url=scratch_database_url)

    # Act
    with patch("trianglebahaiinstitute.db.get_settings", return_value=settings):
        db.run_migrations()
        db.run_migrations()

    # Assert
    head = ScriptDirectory.from_config(
        _alembic_config(scratch_database_url)
    ).get_current_head()
    engine = create_engine(scratch_database_url)
    try:
        with engine.connect() as conn:
            version = conn.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()
    finally:
        engine.dispose()
    assert version == head


def test_concurrent_run_migrations_do_not_conflict(
    scratch_database_url: str,
) -> None:
    # Arrange
    env = {**os.environ, "ENVIRONMENT": "test", "TEST_DATABASE_URL": scratch_database_url}
    code = "from trianglebahaiinstitute.db import run_migrations; run_migrations()"

    # Act
    procs = [
        subprocess.Popen(
            [sys.executable, "-c", code],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        for _ in range(4)
    ]
    results = [(p.communicate(timeout=60)[0], p.returncode) for p in procs]

    # Assert
    assert [rc for _, rc in results] == [0, 0, 0, 0], results
    command.check(_alembic_config(scratch_database_url))


def test_migrations_have_a_single_head() -> None:
    # Arrange
    script = ScriptDirectory.from_config(Config(str(db._ALEMBIC_INI)))

    # Act
    heads = script.get_heads()

    # Assert
    assert len(heads) == 1
