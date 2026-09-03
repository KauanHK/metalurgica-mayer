"""Ambiente de execução das migrations.

Os imports de models abaixo parecem inúteis e não são: o autogenerate compara o
banco com `Base.metadata`, e uma tabela só entra nesse metadata se o módulo que
a declara tiver sido importado. Módulo novo sem import aqui = tabela que o
Alembic acha que precisa **apagar**.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection, pool
from sqlalchemy.ext.asyncio import async_engine_from_config

import app.modules.clients.adapters.db.models
import app.modules.users.adapters.db.models  # noqa: F401
from app.core.db.base import Base
from app.core.settings import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# A URL vem das settings da aplicação, não do alembic.ini: um só lugar define
# contra qual banco tudo roda.
config.set_main_option("sqlalchemy.url", settings.sqlalchemy_database_uri)


def run_migrations_offline() -> None:
    """Gera o SQL das migrations sem conectar ao banco (`alembic upgrade --sql`)."""

    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Sem isto, mudar o tipo de uma coluna não aparece no autogenerate.
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Aplica as migrations conectando ao banco (o caminho normal)."""

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
