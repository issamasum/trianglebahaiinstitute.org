# Copyright (c) 2026 Kris Jordan
# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

"""Drop and recreate the development database, then rebuild all tables.

After recreating tables the script inserts a small set of seed data so the
application is immediately usable for local development and end-to-end tests:

* One user: Carrie  Caretake.
* One tool: Check-in at TBI.
* Event --> List of Visitor.
"""

import sys

import trianglebahaiinstitute.tables  # noqa: F401
from trianglebahaiinstitute.config import Settings
from trianglebahaiinstitute.db import get_engine, reset_db_and_tables
from trianglebahaiinstitute.dev_data import seed
from sqlmodel import Session


def main() -> None:
    """Reset the development database and insert seed data."""
    settings = Settings()

    if settings.environment != "development":
        print("This script can only be run in development.", file=sys.stderr)
        print("Add ENVIRONMENT=development to your .env file.", file=sys.stderr)
        raise SystemExit(1)

    reset_db_and_tables()

    with Session(get_engine()) as session:
        seed(session)
        session.commit()

    print("Reset database and seeded development data.")


if __name__ == "__main__":
    main()
