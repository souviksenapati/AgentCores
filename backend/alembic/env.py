"""
Alembic Configuration for Enterprise Database Migrations
Built for MVP simplicity, designed for billion-dollar platform scale.
"""

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Import our models
from app.models.database import Base

# This is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging (if present)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for autogenerate support
target_metadata = Base.metadata


# Enterprise database URL configuration
def get_database_url():
    """Get database URL from environment variables with enterprise fallbacks"""

    # Primary: Full database URL
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    # Fallback: Individual components
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "agentcores")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine, though an Engine is acceptable here as well.
    By skipping the Engine creation we don't even need a DBAPI to be available.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Enterprise features
        compare_type=True,
        compare_server_default=True,
        render_as_batch=True,  # For SQLite compatibility during development
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection with the context.
    """

    # Override the sqlalchemy.url in the alembic.ini with our environment variable
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        # Enterprise connection settings
        pool_pre_ping=True,  # Validate connections before use
        pool_recycle=3600,  # Recycle connections every hour
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Enterprise migration features
            compare_type=True,
            compare_server_default=True,
            include_schemas=True,
            # Transaction per migration for better rollback support
            transaction_per_migration=True,
            # Custom naming convention for indexes and constraints
            render_item=render_item_with_enterprise_naming,
        )

        with context.begin_transaction():
            context.run_migrations()


def render_item_with_enterprise_naming(type_, obj, autogen_context):
    """
    Custom naming convention for enterprise database objects.

    Ensures consistent naming across environments and database types.
    """
    if type_ == "index":
        # Ensure index names are prefixed consistently
        if not obj.name.startswith("ix_"):
            obj.name = f"ix_{obj.name}"

    elif type_ == "foreign_key":
        # Ensure foreign key names are descriptive
        if not obj.name.startswith("fk_"):
            table_name = obj.parent.name
            column_name = obj.column_keys[0]
            obj.name = f"fk_{table_name}_{column_name}"

    elif type_ == "unique_constraint":
        # Ensure unique constraint names are clear
        if not obj.name.startswith("uq_"):
            table_name = obj.parent.name
            column_name = "_".join(obj.columns.keys())
            obj.name = f"uq_{table_name}_{column_name}"

    # Return None to use default rendering
    return None


# Determine which mode to run migrations in
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
