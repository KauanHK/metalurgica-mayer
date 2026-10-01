from typing import Any

import sqlalchemy as sa

from app.core.db.repository import BaseRepository
from app.modules.service_requests.adapters.db.models import (
    ServiceRequest as ServiceRequestModel,
)
from app.modules.service_requests.application.dtos.filters import (
    ServiceRequestFilters,
)
from app.modules.service_requests.domain.entities import ServiceRequest


class ServiceRequestsRepository(
    BaseRepository[ServiceRequestModel, ServiceRequest, ServiceRequestFilters]
):
    model = ServiceRequestModel
    filters_type = ServiceRequestFilters

    def _to_entity(self, row: ServiceRequestModel) -> ServiceRequest:
        return ServiceRequest(
            id=row.id,
            client_id=row.client_id,
            client_name=row.client.name,
            title=row.title,
            description=row.description,
            status=row.status,
            origin=row.origin,
            requested_at=row.requested_at,
            due_date=row.due_date,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def _apply_filters(
        self, stmt: sa.Select[Any], filters: ServiceRequestFilters
    ) -> sa.Select[Any]:
        if filters.client_id is not None:
            stmt = stmt.where(ServiceRequestModel.client_id == filters.client_id)
        if filters.status is not None:
            stmt = stmt.where(ServiceRequestModel.status == filters.status)
        if filters.origin is not None:
            stmt = stmt.where(ServiceRequestModel.origin == filters.origin)
        if filters.date_from is not None:
            stmt = stmt.where(ServiceRequestModel.requested_at >= filters.date_from)
        if filters.date_to is not None:
            stmt = stmt.where(ServiceRequestModel.requested_at <= filters.date_to)
        if filters.search:
            stmt = stmt.where(
                ServiceRequestModel.title.ilike(f"%{filters.search.strip()}%")
            )
        # Mais recentes primeiro; o `id` desempata solicitações do mesmo dia para
        # que duas páginas seguidas não repitam nem pulem registros.
        return stmt.order_by(
            ServiceRequestModel.requested_at.desc(), ServiceRequestModel.id.asc()
        )
