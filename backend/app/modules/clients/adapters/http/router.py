"""Rotas de clientes — o CRUD-piloto que valida a stack de ponta a ponta.

⚠️ **Sem autenticação nesta sprint.** O cronograma põe login e proteção de rotas
na Sprint 2; a fundação (`app/core/security`, tabela `users`, seed do admin) já
está pronta, e proteger este módulo será acrescentar
`dependencies=[Depends(get_current_actor)]` ao `APIRouter` abaixo, uma linha,
sem tocar em use case nenhum. Até lá a API não deve ser exposta fora da rede
local.
"""

import uuid

from fastapi import APIRouter, status

from app.core.pagination.dependencies import PageParamsDep
from app.core.pagination.schemas import PaginatedResponse, build_paginated_response
from app.modules.clients.adapters.http.dependencies import (
    ClientsUnitOfWorkDep,
    PaginationFiltersDep,
)
from app.modules.clients.adapters.http.schemas import (
    ClientCreate,
    ClientRead,
    ClientUpdate,
)
from app.modules.clients.application.dtos.commands import (
    CreateClientCommand,
    UpdateClientCommand,
)
from app.modules.clients.application.use_cases.clients_creator import ClientsCreator
from app.modules.clients.application.use_cases.clients_deleter import ClientsDeleter
from app.modules.clients.application.use_cases.clients_paginator import ClientsPaginator
from app.modules.clients.application.use_cases.clients_reader import ClientsReader
from app.modules.clients.application.use_cases.clients_updater import ClientsUpdater

router = APIRouter()


@router.get("", response_model=PaginatedResponse[ClientRead], summary="Listar clientes")
async def list_clients(
    filters: PaginationFiltersDep,
    page_params: PageParamsDep,
    uow: ClientsUnitOfWorkDep,
) -> PaginatedResponse[ClientRead]:
    """Lista clientes com busca livre e paginação."""

    page = await ClientsPaginator(uow=uow).paginate(
        page_params=page_params, filters=filters
    )
    return build_paginated_response(
        items=[ClientRead.model_validate(c.to_dict()) for c in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
    )


@router.post(
    "",
    response_model=ClientRead,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar cliente",
)
async def create_client(data: ClientCreate, uow: ClientsUnitOfWorkDep) -> ClientRead:
    """Cadastra um cliente. Recusa com 409 documento já usado por outro."""

    client = await ClientsCreator(uow=uow).create(
        CreateClientCommand(**data.model_dump())
    )
    return ClientRead.model_validate(client.to_dict())


@router.get("/{client_id}", response_model=ClientRead, summary="Consultar cliente")
async def get_client(client_id: uuid.UUID, uow: ClientsUnitOfWorkDep) -> ClientRead:
    """Devolve um cliente pelo id."""

    client = await ClientsReader(uow=uow).get_by_id(client_id)
    return ClientRead.model_validate(client.to_dict())


@router.patch("/{client_id}", response_model=ClientRead, summary="Editar cliente")
async def update_client(
    client_id: uuid.UUID,
    data: ClientUpdate,
    uow: ClientsUnitOfWorkDep,
) -> ClientRead:
    """Altera apenas os campos enviados no corpo."""

    client = await ClientsUpdater(uow=uow).update(
        client_id,
        # `exclude_unset` é o que preserva a semântica do PATCH: campo ausente
        # vira `UNSET` no comando, campo enviado como `null` apaga o valor.
        UpdateClientCommand(**data.model_dump(exclude_unset=True)),
    )
    return ClientRead.model_validate(client.to_dict())


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir cliente",
)
async def delete_client(client_id: uuid.UUID, uow: ClientsUnitOfWorkDep) -> None:
    """Exclui um cliente sem histórico; com histórico, recusa com 409."""

    await ClientsDeleter(uow=uow).delete(client_id)
