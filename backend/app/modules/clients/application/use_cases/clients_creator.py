from app.core.exceptions import ConflictError
from app.modules.clients.application.dtos.commands import CreateClientCommand
from app.modules.clients.application.ports.unit_of_work import ClientsUnitOfWorkProtocol
from app.modules.clients.domain.entities import Client, NewClient


class ClientsCreator:
    """Cadastra um cliente novo."""

    def __init__(self, uow: ClientsUnitOfWorkProtocol) -> None:
        self._uow = uow

    async def create(self, data: CreateClientCommand) -> Client:
        async with self._uow as uow:
            if data.document is not None:
                existing = await uow.clients.get_by_document_or_none(data.document)
                if existing is not None:
                    raise ConflictError(
                        f"Já existe um cliente com o documento {data.document}."
                    )
            return await uow.clients.create(
                NewClient(
                    name=data.name,
                    document=data.document,
                    phone=data.phone,
                    email=data.email,
                    zip_code=data.zip_code,
                    street=data.street,
                    number=data.number,
                    complement=data.complement,
                    neighborhood=data.neighborhood,
                    city=data.city,
                    state=data.state,
                    notes=data.notes,
                    is_active=data.is_active,
                )
            )
