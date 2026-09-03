import uuid

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError
from app.modules.clients.application.ports.unit_of_work import ClientsUnitOfWorkProtocol


class ClientsDeleter:
    """Exclui um cliente sem histórico.

    Cliente com solicitações vinculadas não é excluído: a FK de
    `service_requests` é `RESTRICT`, e o `IntegrityError` que ela levanta vira um
    409 explicando o motivo. Quem tem histórico é desativado (`is_active`), e é
    isso que a mensagem sugere.
    """

    def __init__(self, uow: ClientsUnitOfWorkProtocol) -> None:
        self._uow = uow

    async def delete(self, id_: uuid.UUID) -> None:
        try:
            async with self._uow as uow:
                await uow.clients.delete(id_)
        except IntegrityError as err:
            raise ConflictError(
                "Este cliente possui solicitações vinculadas e não pode ser "
                "excluído. Desative o cadastro para tirá-lo da operação sem "
                "perder o histórico."
            ) from err
