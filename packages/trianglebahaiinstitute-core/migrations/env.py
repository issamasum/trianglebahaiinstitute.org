"""Alembic environment: wires migrations to the app's settings and models."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool, text
from sqlmodel import SQLModel

from trianglebahaiinstitute.config import get_settings
from trianglebahaiinstitute.db import load_table_metadata

# Arbitrary constant identifying this app's migration lock in pg_advisory_lock.
MIGRATION_LOCK_KEY = 7_450_218_331

config = context.config
if config.config_file_name is not None:
    # Keep the app's own loggers alive when migrations run in-process.
    fileConfig(config.config_file_name, disable_existing_loggers=False)

load_table_metadata()
target_metadata = SQLModel.metadata

_current_url = config.get_main_option("sqlalchemy.url")
if not _current_url or _current_url.startswith("driver://"):
    config.set_main_option(
        "sqlalchemy.url", get_settings().effective_database_url.replace("%", "%%")
    )


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            # include_schemas=True,  # enable if any tables use a non-default schema
        )
        with context.begin_transaction():
            if connection.dialect.name == "postgresql":
                connection.execute(
                    text("SELECT pg_advisory_xact_lock(:key)"),
                    {"key": MIGRATION_LOCK_KEY},
                )
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
