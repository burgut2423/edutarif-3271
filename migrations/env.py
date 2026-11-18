"""Alembic environment for EduTarif (SQLite dev / PostgreSQL production).

Migration config must never auto-create/drop application tables outside migrations.
"""
import os
from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine, pool
from app.db import Base, DATABASE_URL
import app.models  # noqa: F401 - register all declarative models

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url():
    # Config.attributes allows tests to point at a disposable database.
    return config.attributes.get("database_url") or os.environ.get("DATABASE_URL") or DATABASE_URL


def run_migrations_offline():
    context.configure(url=get_url(), target_metadata=target_metadata,
                      literal_binds=True, dialect_opts={"paramstyle": "named"},
                      compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    # Re-use a caller-supplied connection when testing transactional migrations.
    supplied = config.attributes.get("connection")
    if supplied is not None:
        context.configure(connection=supplied, target_metadata=target_metadata,
                          compare_type=True, render_as_batch=supplied.dialect.name == "sqlite")
        with context.begin_transaction():
            context.run_migrations()
        return

    engine = create_engine(get_url(), poolclass=pool.NullPool,
                           pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata,
                              compare_type=True, render_as_batch=connection.dialect.name == "sqlite")
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
