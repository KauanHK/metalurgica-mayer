import uuid

from app.modules.users.application.dtos.commands import UpdateProfileCommand
from app.modules.users.application.ports.unit_of_work import UsersUnitOfWorkProtocol
from app.modules.users.domain.entities import UpdateUser, User


class UsersUpdater:
    """Altera os campos informados do próprio perfil."""

    def __init__(self, uow: UsersUnitOfWorkProtocol) -> None:
        self._uow = uow

    async def update(self, id_: uuid.UUID, data: UpdateProfileCommand) -> User:
        async with self._uow as uow:
            return await uow.users.update(id_, UpdateUser(**data.defined_values()))
