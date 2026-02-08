import asyncio
from logging.config import fileConfig
import sys
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from sqlmodel import SQLModel

# To find /backend/app
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Settings n Models
from app.core.config import settings

# Current models to migrate
from app.modules.inventory.models import Product
from app.modules.sellers.models import Seller
from app.modules.orders.models import Order, OrderDetail
from app.modules.refunds.models import Refund, RefundDetail
# from app.modules.auth.models import User

# Alembic base config
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# My postgres path with "+asyncpg"
config.set_main_option("sqlalchemy.url", str(settings.SQLALCHEMY_DATABASE_URI))

target_metadata = SQLModel.metadata

# Migration func
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection):
    """Ejecuta las migraciones de forma síncrona sobre una conexión."""
    context.configure(
        connection=connection, 
        target_metadata=target_metadata,
        compare_type=True,          # To update column changes
        compare_server_default=True # To update default values changes
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode (Async)."""
    
    # Create async engine
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # run_sync for alembic syncs (not async)
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

# Entrypoint
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())