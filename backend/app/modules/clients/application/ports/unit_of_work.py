from types import TracebackType
from typing import Protocol, Self

from app.modules.clients.application.ports.repository import ClientsRepositoryProtocol


class ClientsUnitOfWorkProtocol(Protocol):
    """Transação que expõe o repositório de clientes."""

    @property
    def clients(self) -> ClientsRepositoryProtocol: ...

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
