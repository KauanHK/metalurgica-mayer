from collections.abc import Callable
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.unit_of_work import BaseUnitOfWork
from app.modules.clients.adapters.db.repository import ClientsRepository
from app.modules.service_requests.adapters.db.repository import (
    ServiceRequestsRepository,
)


class ServiceRequestsUnitOfWork(BaseUnitOfWork):
    """Transação do módulo de solicitações.

    Expõe também o repositório de clientes, só para a validação de que o cliente
    existe e está ativo acontecer na mesma transação da criação.
    """

    def __init__(self, session_factory: Callable[[], AsyncSession]) -> None:
        super().__init__(session_factory=session_factory)
        self._service_requests: ServiceRequestsRepository | None = None
        self._clients: ClientsRepository | None = None

    @property
    def service_requests(self) -> ServiceRequestsRepository:
        if self._service_requests is None:
            raise RuntimeError(
                "Repositório de solicitações indisponível fora do context manager."
            )
        return self._service_requests

    @property
    def clients(self) -> ClientsRepository:
        if self._clients is None:
            raise RuntimeError(
                "Repositório de clientes indisponível fora do context manager."
            )
        return self._clients

    async def __aenter__(self) -> Self:
        await super().__aenter__()
        self._service_requests = ServiceRequestsRepository(self.session)
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
            self._service_requests = None
            self._clients = None
