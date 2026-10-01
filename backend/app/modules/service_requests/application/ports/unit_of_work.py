from types import TracebackType
from typing import Protocol, Self

from app.modules.service_requests.application.ports.repository import (
    ClientsLookupProtocol,
    ServiceRequestsRepositoryProtocol,
)


class ServiceRequestsUnitOfWorkProtocol(Protocol):
    """Transação que expõe o repositório de solicitações e a consulta a clientes."""

    @property
    def service_requests(self) -> ServiceRequestsRepositoryProtocol: ...

    @property
    def clients(self) -> ClientsLookupProtocol: ...

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
