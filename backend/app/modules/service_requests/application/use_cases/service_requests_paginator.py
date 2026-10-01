import uuid
from dataclasses import replace

from app.core.exceptions import NotFoundError
from app.core.pagination.params import Page, PageParams
from app.modules.service_requests.application.dtos.filters import (
    ServiceRequestFilters,
)
from app.modules.service_requests.application.ports.unit_of_work import (
    ServiceRequestsUnitOfWorkProtocol,
)
from app.modules.service_requests.domain.entities import ServiceRequest


class ServiceRequestsPaginator:
    """Lista solicitações com filtros e paginação."""

    def __init__(self, uow: ServiceRequestsUnitOfWorkProtocol) -> None:
        self._uow = uow

    async def paginate(
        self,
        page_params: PageParams,
        filters: ServiceRequestFilters | None = None,
    ) -> Page[ServiceRequest]:
        async with self._uow as uow:
            return await uow.service_requests.paginate(
                page_params=page_params, filters=filters
            )

    async def paginate_by_client(
        self,
        client_id: uuid.UUID,
        page_params: PageParams,
        filters: ServiceRequestFilters | None = None,
    ) -> Page[ServiceRequest]:
        """Histórico de um cliente; 404 se o cliente não existe.

        Sem a checagem, um id inexistente devolveria uma lista vazia — igual à
        de um cliente que simplesmente ainda não pediu nada.
        """

        async with self._uow as uow:
            if await uow.clients.get_by_id_or_none(client_id) is None:
                raise NotFoundError(f"Cliente com ID {client_id} não encontrado.")
            return await uow.service_requests.paginate(
                page_params=page_params,
                filters=replace(
                    filters or ServiceRequestFilters(), client_id=client_id
                ),
            )
