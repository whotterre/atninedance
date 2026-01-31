from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from api.v1.models.base_model import Base

# Use the DeclarativeBase metadata from your models so alembic autogenerate works
target_metadata = Base.metadata

# Allow overriding the DB URL via the DATABASE_URL environment variable.
# If set, this will replace the sqlalchemy.url value from alembic.ini.
if os.environ.get("DATABASE_URL"):
    config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

# Import model modules so that declarative models are registered on Base.metadata.
# Without importing the modules, `autogenerate` will see an empty metadata.
try:
    import importlib
    MODEL_MODULES = [
        "api.v1.models.student",
        "api.v1.models.student_face_record",
        "api.v1.models.att_session",
        "api.v1.models.att_record",
    ]
    for m in MODEL_MODULES:
        try:
            importlib.import_module(m)
        except Exception:
            # ignore: module may have optional deps or runtime requirements
            pass
except Exception:
    pass

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
