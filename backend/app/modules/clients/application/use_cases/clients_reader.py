import uuid

from app.modules.clients.application.ports.unit_of_work import ClientsUnitOfWorkProtocol
from app.modules.clients.domain.entities import Client


class ClientsReader:
    """Lê um cliente pelo id."""

    def __init__(self, uow: ClientsUnitOfWorkProtocol) -> None:
        self._uow = uow

    async def get_by_id(self, id_: uuid.UUID) -> Client:
        async with self._uow as uow:
            return await uow.clients.get_by_id(id_)
