import uuid

from app.core.exceptions import ConflictError
from app.core.types import is_unset
from app.modules.clients.application.dtos.commands import UpdateClientCommand
from app.modules.clients.application.ports.unit_of_work import ClientsUnitOfWorkProtocol
from app.modules.clients.domain.entities import Client, UpdateClient


class ClientsUpdater:
    """Altera os campos informados de um cliente."""

    def __init__(self, uow: ClientsUnitOfWorkProtocol) -> None:
        self._uow = uow

    async def update(self, id_: uuid.UUID, data: UpdateClientCommand) -> Client:
        async with self._uow as uow:
            # `is_unset` e não `is not None`: mandar `document: null` é apagar o
            # documento — operação legítima, e que não precisa de checagem de
            # duplicidade.
            if not is_unset(data.document) and data.document is not None:
                existing = await uow.clients.get_by_document_or_none(str(data.document))
                if existing is not None and existing.id != id_:
                    raise ConflictError(
                        f"O documento {data.document} já pertence a outro cliente."
                    )
            return await uow.clients.update(id_, UpdateClient(**data.defined_values()))
