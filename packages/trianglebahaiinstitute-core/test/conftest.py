# Copyright (c) 2026 Kris Jordan
#  Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from sqlmodel import Session, SQLModel, create_engine

from trianglebahaiinstitute.config import get_settings

DEFAULT_TEST_DB_URL = (
    "postgresql+psycopg://postgres:postgres@postgres:5432/trianglebahaiinstitute_test"
)
TEST_DB_URL = os.environ.get("TEST_DATABASE_URL", DEFAULT_TEST_DB_URL)


@pytest.fixture(autouse=True)
def clear_settings_cache() -> Iterator[None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture()
def session():
    """Provide a transactional session that rolls back after each test."""
    engine = create_engine(TEST_DB_URL)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
        session.rollback()
