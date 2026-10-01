import uuid

from app.modules.service_requests.application.ports.unit_of_work import (
    ServiceRequestsUnitOfWorkProtocol,
)
from app.modules.service_requests.domain.entities import ServiceRequest


class ServiceRequestsReader:
    """Lê uma solicitação pelo id."""

    def __init__(self, uow: ServiceRequestsUnitOfWorkProtocol) -> None:
        self._uow = uow

    async def get_by_id(self, id_: uuid.UUID) -> ServiceRequest:
        async with self._uow as uow:
            return await uow.service_requests.get_by_id(id_)
