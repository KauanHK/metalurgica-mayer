from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.settings import settings


class _Database:
    """Engine e fábrica de sessões, criados no lifespan da aplicação.

    O engine não nasce no import: a app precisa poder ser importada sem banco
    (coleta de testes, `alembic`, geração do OpenAPI). Quem o inicializa é
    `db.init()`, chamado no lifespan (ver `app/core/startup.py`).
    """

    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    def is_initialized(self) -> bool:
        """Indica se o engine e a fábrica de sessões já existem."""

        return self._engine is not None and self._session_factory is not None

    def init(self) -> None:
        """Cria o engine e a fábrica de sessões, se ainda não existirem."""

        if self.is_initialized():
            return

        self._engine = create_async_engine(
            settings.sqlalchemy_database_uri,
            # O Postgres do compose reinicia; sem o pre-ping a primeira query
            # depois disso morre numa conexão que o pool ainda julga viva.
            pool_pre_ping=True,
            future=True,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def close(self) -> None:
        """Fecha o pool de conexões."""

        if self._engine is None:
            return

        await self._engine.dispose()
        self._engine = None
        self._session_factory = None

    def create_session(self) -> AsyncSession:
        """Cria uma sessão assíncrona nova."""

        if self._session_factory is None:
            raise RuntimeError("Engine do banco de dados não inicializado.")
        return self._session_factory()

    async def session_context(self) -> AsyncGenerator[AsyncSession]:
        """Fornece uma sessão assíncrona e a fecha ao final."""

        async with self.create_session() as session:
            yield session


db = _Database()
