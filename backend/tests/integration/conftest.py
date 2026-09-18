"""Fixtures de infraestrutura dos testes de integração.

Cada teste roda dentro de uma conexão com uma transação externa que nunca é
commitada de verdade. As sessões que os use cases abrem durante o teste (via
`app.dependency_overrides`) são presas a essa mesma conexão com
`join_transaction_mode="create_savepoint"`: o `commit()` que o
`BaseUnitOfWork` chama ao sair do `async with` fecha só um SAVEPOINT, nunca a
transação de verdade. O rollback no fim do teste desfaz tudo — inclusive o que
os próprios use cases "commitaram" —, o que deixa o banco limpo entre testes
sem recriar o schema a cada um.

Pressupõe um Postgres com as migrations aplicadas (é o que o CI faz antes de
rodar o pytest; localmente, `alembic upgrade head` primeiro).
"""

from collections.abc import AsyncGenerator, Callable, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.settings import settings
from app.modules.clients.adapters.db.factories import (
    make_unit_of_work as make_clients_uow,
)
from app.modules.clients.adapters.db.unit_of_work import ClientsUnitOfWork
from app.modules.users.adapters.db.factories import make_unit_of_work as make_users_uow
from app.modules.users.adapters.db.unit_of_work import UsersUnitOfWork


@pytest_asyncio.fixture
async def db_connection() -> AsyncGenerator[AsyncConnection]:
    """Uma conexão com uma transação externa que nunca é commitada de verdade."""

    engine = create_async_engine(settings.sqlalchemy_database_uri)
    async with engine.connect() as connection:
        await connection.begin()
        yield connection
        await connection.rollback()
    await engine.dispose()


@pytest.fixture
def session_factory(
    db_connection: AsyncConnection,
) -> Callable[[], AsyncSession]:
    """Fábrica de sessões presas à mesma conexão/transação do teste."""

    return async_sessionmaker(
        bind=db_connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )


@pytest.fixture(autouse=True)
def _override_unit_of_work_factories(
    session_factory: Callable[[], AsyncSession],
) -> Generator[None]:
    """Troca as fábricas de UoW dos módulos pela presa à transação do teste."""

    from app.main import app

    app.dependency_overrides[make_clients_uow] = lambda: ClientsUnitOfWork(
        session_factory=session_factory
    )
    app.dependency_overrides[make_users_uow] = lambda: UsersUnitOfWork(
        session_factory=session_factory
    )
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    """Cliente HTTP assíncrono contra a aplicação, sem subir um servidor de verdade."""

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test/api") as ac:
        yield ac
