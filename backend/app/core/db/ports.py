import uuid
from typing import Protocol

from app.core.pagination.params import Page, PageParams
from app.core.types import BaseCreateCommand, BaseUpdateCommand, DataclassInstance


class ReadRepositoryProtocol[EntityT](Protocol):
    """Contrato mínimo de leitura.

    Existe separado para que um use case que só lê dependa apenas disto, e não
    do CRUD inteiro.
    """

    async def get_by_id_or_none(self, id_: uuid.UUID) -> EntityT | None: ...
    async def get_by_id(self, id_: uuid.UUID) -> EntityT: ...


class BaseRepositoryProtocol[
    EntityT,
    FiltersT: DataclassInstance,
    CreateCommandT: BaseCreateCommand,
    UpdateCommandT: BaseUpdateCommand,
](ReadRepositoryProtocol[EntityT], Protocol):
    """Contrato completo de CRUD + paginação.

    `BaseRepository` o satisfaz **estruturalmente**, sem herdar: os módulos
    especializam os parâmetros com seus próprios tipos e acrescentam só os
    métodos específicos do domínio.
    """

    async def create(self, create_command: CreateCommandT) -> EntityT: ...
    async def update(
        self, id_: uuid.UUID, update_command: UpdateCommandT
    ) -> EntityT: ...
    async def delete(self, id_: uuid.UUID) -> None: ...
    async def paginate(
        self,
        page_params: PageParams,
        filters: FiltersT | None = None,
    ) -> Page[EntityT]: ...
