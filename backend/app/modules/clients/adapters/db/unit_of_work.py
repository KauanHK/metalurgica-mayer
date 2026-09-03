from collections.abc import Callable
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.unit_of_work import BaseUnitOfWork
from app.modules.clients.adapters.db.repository import ClientsRepository


class ClientsUnitOfWork(BaseUnitOfWork):
    """Transação do módulo de clientes."""

    def __init__(self, session_factory: Callable[[], AsyncSession]) -> None:
        super().__init__(session_factory=session_factory)
        self._clients: ClientsRepository | None = None

    @property
    def clients(self) -> ClientsRepository:
        if self._clients is None:
            raise RuntimeError(
                "Repositório de clientes indisponível fora do context manager."
            )
        return self._clients

    async def __aenter__(self) -> Self:
        await super().__aenter__()
        self._clients = ClientsRepository(self.session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        try:
            await super().__aexit__(exc_type, exc_val, exc_tb)
        finally:
            self._clients = None
