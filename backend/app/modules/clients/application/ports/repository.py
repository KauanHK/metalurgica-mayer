import uuid
from typing import Protocol

from app.core.pagination.params import Page, PageParams
from app.modules.clients.application.dtos.filters import ClientFilters
from app.modules.clients.domain.entities import Client, NewClient, UpdateClient


class ClientsRepositoryProtocol(Protocol):
    """O que os use cases de clientes precisam do repositório.

    `ClientsRepository` o satisfaz estruturalmente, sem herdar: o contrato é o
    que a aplicação usa, não o que o adaptador oferece.
    """

    async def get_by_id(self, id_: uuid.UUID) -> Client: ...
    async def get_by_id_or_none(self, id_: uuid.UUID) -> Client | None: ...
    async def get_by_document_or_none(self, document: str) -> Client | None: ...
    async def create(self, create_command: NewClient) -> Client: ...
    async def update(self, id_: uuid.UUID, update_command: UpdateClient) -> Client: ...
    async def delete(self, id_: uuid.UUID) -> None: ...
    async def paginate(
        self,
        page_params: PageParams,
        filters: ClientFilters | None = None,
    ) -> Page[Client]: ...
