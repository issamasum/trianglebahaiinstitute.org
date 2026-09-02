# Copyright (c) 2026 Kris Jordan
# Copyright (c) 2026 Issa Masumbuko
# SPDX-License-Identifier: MIT

import sys

import trianglebahaiinstitute.tables  # noqa: F401
from trianglebahaiinstitute.config import Settings
from trianglebahaiinstitute.db import create_db_and_tables

settings = Settings()

if settings.environment != "development":
    print("This script can only be run in development.", file=sys.stderr)
    print("Add ENVIRONMENT=development to your .env file.", file=sys.stderr)
    exit(1)


create_db_and_tables()
print("Created Database and Tables")
