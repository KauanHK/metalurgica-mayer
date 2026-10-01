import uuid
from typing import Protocol

from app.core.pagination.params import Page, PageParams
from app.modules.clients.domain.entities import Client, NewClient
from app.modules.service_requests.application.dtos.filters import (
    ServiceRequestFilters,
)
from app.modules.service_requests.domain.entities import (
    NewServiceRequest,
    ServiceRequest,
    UpdateServiceRequest,
)


class ServiceRequestsRepositoryProtocol(Protocol):
    """O que os use cases de solicitações precisam do repositório.

    Não há `delete`: solicitação cancelada fica como `CANCELLED`, e o histórico
    do cliente é preservado.
    """

    async def get_by_id(self, id_: uuid.UUID) -> ServiceRequest: ...
    async def create(self, create_command: NewServiceRequest) -> ServiceRequest: ...
    async def update(
        self, id_: uuid.UUID, update_command: UpdateServiceRequest
    ) -> ServiceRequest: ...
    async def paginate(
        self,
        page_params: PageParams,
        filters: ServiceRequestFilters | None = None,
    ) -> Page[ServiceRequest]: ...


class ClientsLookupProtocol(Protocol):
    """O pouco que as solicitações precisam saber do cadastro de clientes.

    Consultas (`get_*`) servem à validação do fluxo interno e ao vínculo da
    entrada pública; `create` só é usado pela entrada pública, que cadastra o
    solicitante quando ele ainda não é cliente.
    """

    async def get_by_id_or_none(self, id_: uuid.UUID) -> Client | None: ...
    async def get_by_document_or_none(self, document: str) -> Client | None: ...
    async def get_by_email_or_none(self, email: str) -> Client | None: ...
    async def create(self, create_command: NewClient) -> Client: ...
