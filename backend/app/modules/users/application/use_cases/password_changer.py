import uuid

from app.core.exceptions import UnauthorizedError
from app.core.security.passwords import hash_password, verify_password
from app.modules.users.application.dtos.commands import ChangePasswordCommand
from app.modules.users.application.ports.unit_of_work import UsersUnitOfWorkProtocol


class PasswordChanger:
    """Troca a senha de um usuário, mediante a senha atual."""

    def __init__(self, uow: UsersUnitOfWorkProtocol) -> None:
        self._uow = uow

    async def change(self, id_: uuid.UUID, data: ChangePasswordCommand) -> None:
        async with self._uow as uow:
            credentials = await uow.users.get_credentials_by_id(id_)
            if not verify_password(data.current_password, credentials.password_hash):
                raise UnauthorizedError("Senha atual incorreta.")
            await uow.users.set_password_hash(id_, hash_password(data.new_password))
