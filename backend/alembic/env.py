from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# استيراد Base و DATABASE_URL من مشروعك
from app.database import Base, DATABASE_URL

# استيراد المودلز عشان يتسجلوا في metadata
from app.models import *

# Alembic Config
config = context.config

# ربط DATABASE_URL من مشروعك مع Alembic
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# إعداد اللوج
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# مهم جداً: ربط metadata
target_metadata = Base.metadata


# -----------------------------
# Offline Mode
# -----------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # يكشف تغيير نوع الأعمدة
    )

    with context.begin_transaction():
        context.run_migrations()


# -----------------------------
# Online Mode (Async)
# -----------------------------
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # يكشف تغيير نوع الأعمدة
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async engine."""

    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# -----------------------------
# تشغيل الوضع المناسب
# -----------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())