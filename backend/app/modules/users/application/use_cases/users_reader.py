import uuid

from app.modules.users.application.ports.unit_of_work import UsersUnitOfWorkProtocol
from app.modules.users.domain.entities import User


class UsersReader:
    """Lê um usuário pelo id."""

    def __init__(self, uow: UsersUnitOfWorkProtocol) -> None:
        self._uow = uow

    async def get_by_id(self, id_: uuid.UUID) -> User:
        async with self._uow as uow:
            return await uow.users.get_by_id(id_)
