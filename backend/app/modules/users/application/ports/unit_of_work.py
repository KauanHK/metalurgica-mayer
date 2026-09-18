from types import TracebackType
from typing import Protocol, Self

from app.modules.users.application.ports.repository import UsersRepositoryProtocol


class UsersUnitOfWorkProtocol(Protocol):
    """Transação que expõe o repositório de usuários."""

    @property
    def users(self) -> UsersRepositoryProtocol: ...

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
