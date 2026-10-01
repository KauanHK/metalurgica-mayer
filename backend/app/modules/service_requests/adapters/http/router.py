"""Rotas de solicitações de serviço.

Protegidas por `get_current_actor`: exigem um token de acesso válido de um
usuário ativo. Não há `DELETE` — a solicitação que não vai adiante é cancelada
(`status = cancelled`) e continua no histórico do cliente.

Dois routers saem daqui porque os prefixos são diferentes: `router`
(`/service-requests`) e `client_history_router` (`/clients/{id}/service-requests`),
que mostra o histórico na ficha do cliente sem o módulo de clientes precisar
conhecer o de solicitações.
"""

import uuid

from fastapi import APIRouter, Depends, status

from app.core.pagination.dependencies import PageParamsDep
from app.core.pagination.schemas import PaginatedResponse, build_paginated_response
from app.modules.service_requests.adapters.http.dependencies import (
    ClientHistoryFiltersDep,
    PaginationFiltersDep,
    ServiceRequestsUnitOfWorkDep,
)
from app.modules.service_requests.adapters.http.schemas import (
    ServiceRequestCreate,
    ServiceRequestRead,
    ServiceRequestUpdate,
)
from app.modules.service_requests.application.dtos.commands import (
    CreateServiceRequestCommand,
    UpdateServiceRequestCommand,
)
from app.modules.service_requests.application.use_cases.service_requests_creator import (  # noqa: E501
    ServiceRequestsCreator,
)
from app.modules.service_requests.application.use_cases.service_requests_paginator import (  # noqa: E501
    ServiceRequestsPaginator,
)
from app.modules.service_requests.application.use_cases.service_requests_reader import (
    ServiceRequestsReader,
)
from app.modules.service_requests.application.use_cases.service_requests_updater import (  # noqa: E501
    ServiceRequestsUpdater,
)
from app.modules.users.adapters.http.dependencies import get_current_actor

router = APIRouter(dependencies=[Depends(get_current_actor)])
client_history_router = APIRouter(dependencies=[Depends(get_current_actor)])


@router.get(
    "",
    response_model=PaginatedResponse[ServiceRequestRead],
    summary="Listar solicitações",
)
async def list_service_requests(
    filters: PaginationFiltersDep,
    page_params: PageParamsDep,
    uow: ServiceRequestsUnitOfWorkDep,
) -> PaginatedResponse[ServiceRequestRead]:
    """Lista solicitações por cliente, status, período e título, da mais recente."""

    page = await ServiceRequestsPaginator(uow=uow).paginate(
        page_params=page_params, filters=filters
    )
    return build_paginated_response(
        items=[ServiceRequestRead.model_validate(s.to_dict()) for s in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
    )


@router.post(
    "",
    response_model=ServiceRequestRead,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar solicitação",
)
async def create_service_request(
    data: ServiceRequestCreate, uow: ServiceRequestsUnitOfWorkDep
) -> ServiceRequestRead:
    """Registra uma solicitação para um cliente ativo; nasce com status `open`."""

    service_request = await ServiceRequestsCreator(uow=uow).create(
        CreateServiceRequestCommand(**data.model_dump())
    )
    return ServiceRequestRead.model_validate(service_request.to_dict())


@router.get(
    "/{service_request_id}",
    response_model=ServiceRequestRead,
    summary="Consultar solicitação",
)
async def get_service_request(
    service_request_id: uuid.UUID, uow: ServiceRequestsUnitOfWorkDep
) -> ServiceRequestRead:
    """Devolve uma solicitação pelo id."""

    service_request = await ServiceRequestsReader(uow=uow).get_by_id(service_request_id)
    return ServiceRequestRead.model_validate(service_request.to_dict())


@router.patch(
    "/{service_request_id}",
    response_model=ServiceRequestRead,
    summary="Editar solicitação",
)
async def update_service_request(
    service_request_id: uuid.UUID,
    data: ServiceRequestUpdate,
    uow: ServiceRequestsUnitOfWorkDep,
) -> ServiceRequestRead:
    """Altera apenas os campos enviados; é por aqui que o status muda.

    Solicitação concluída ou cancelada não muda de status (409).
    """

    service_request = await ServiceRequestsUpdater(uow=uow).update(
        service_request_id,
        # `exclude_unset` preserva a semântica do PATCH: ausente = não mexer,
        # `null` = limpar (só vale para `description` e `due_date`).
        UpdateServiceRequestCommand(**data.model_dump(exclude_unset=True)),
    )
    return ServiceRequestRead.model_validate(service_request.to_dict())


@client_history_router.get(
    "/{client_id}/service-requests",
    response_model=PaginatedResponse[ServiceRequestRead],
    summary="Histórico de solicitações do cliente",
)
async def list_client_service_requests(
    client_id: uuid.UUID,
    filters: ClientHistoryFiltersDep,
    page_params: PageParamsDep,
    uow: ServiceRequestsUnitOfWorkDep,
) -> PaginatedResponse[ServiceRequestRead]:
    """Solicitações de um cliente, da mais recente; 404 se o cliente não existe."""

    page = await ServiceRequestsPaginator(uow=uow).paginate_by_client(
        client_id=client_id, page_params=page_params, filters=filters
    )
    return build_paginated_response(
        items=[ServiceRequestRead.model_validate(s.to_dict()) for s in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
    )
