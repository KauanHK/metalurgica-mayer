from typing import Annotated

from fastapi import Depends

from app.core.exceptions import ValidationAppError
from app.modules.service_requests.adapters.db.factories import make_unit_of_work
from app.modules.service_requests.adapters.db.unit_of_work import (
    ServiceRequestsUnitOfWork,
)
from app.modules.service_requests.adapters.http.schemas import (
    ClientServiceRequestsPaginationFilters,
    ServiceRequestsPaginationFilters,
)
from app.modules.service_requests.application.dtos.filters import (
    ServiceRequestFilters,
)

ServiceRequestsUnitOfWorkDep = Annotated[
    ServiceRequestsUnitOfWork, Depends(make_unit_of_work)
]


def _ensure_period_in_order(
    query_params: ClientServiceRequestsPaginationFilters,
) -> None:
    """Recusa período invertido com o mesmo formato de erro dos demais 422.

    Fica aqui, e não em um validator do schema: o `ValidationError` levantado
    dentro de um `Depends()` não passa pelo handler de `RequestValidationError`.
    """

    if (
        query_params.date_from is not None
        and query_params.date_to is not None
        and query_params.date_from > query_params.date_to
    ):
        raise ValidationAppError(
            "A data inicial não pode ser posterior à data final.",
            details=[
                {
                    "field": "date_from",
                    "message": "A data inicial não pode ser posterior à data final.",
                    "type": "value_error",
                }
            ],
        )


def get_pagination_filters(
    query_params: Annotated[ServiceRequestsPaginationFilters, Depends()],
) -> ServiceRequestFilters:
    """Converte os query params no filtro do domínio."""

    _ensure_period_in_order(query_params)
    return ServiceRequestFilters(
        client_id=query_params.client_id,
        status=query_params.status,
        origin=query_params.origin,
        date_from=query_params.date_from,
        date_to=query_params.date_to,
        search=query_params.search,
    )


def get_client_history_filters(
    query_params: Annotated[ClientServiceRequestsPaginationFilters, Depends()],
) -> ServiceRequestFilters:
    """Filtros do histórico de um cliente; o `client_id` é aplicado pelo caminho."""

    _ensure_period_in_order(query_params)
    return ServiceRequestFilters(
        status=query_params.status,
        origin=query_params.origin,
        date_from=query_params.date_from,
        date_to=query_params.date_to,
        search=query_params.search,
    )


PaginationFiltersDep = Annotated[ServiceRequestFilters, Depends(get_pagination_filters)]
ClientHistoryFiltersDep = Annotated[
    ServiceRequestFilters, Depends(get_client_history_filters)
]
