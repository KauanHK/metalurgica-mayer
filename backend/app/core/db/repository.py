import uuid
from abc import ABC, abstractmethod
from typing import Any, cast

import sqlalchemy as sa
from sqlalchemy import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.base import Base
from app.core.exceptions import NotFoundError
from app.core.pagination.params import Page, PageParams
from app.core.types import BaseCreateCommand, BaseUpdateCommand, DataclassInstance


class BaseRepository[
    ModelT: Base,
    EntityT: DataclassInstance,
    FiltersT: DataclassInstance,
](ABC):
    """CRUD e paginação comuns a todos os repositórios.

    A subclasse declara `model` e `filters_type`, implementa `_to_entity` e, se
    a listagem tiver filtros, sobrescreve `_apply_filters`.

    A conversão model → entidade acontece **sempre** na fronteira: nenhum use
    case vê um objeto SQLAlchemy, e por isso nenhum deles pode disparar um lazy
    load acidental fora da sessão.
    """

    model: type[ModelT]
    filters_type: type[FiltersT]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @abstractmethod
    def _to_entity(self, row: ModelT) -> EntityT:
        """Converte uma linha do banco na entidade de domínio."""

    async def get_by_id_or_none(self, id_: uuid.UUID) -> EntityT | None:
        """Busca por ID, devolvendo `None` quando não existe."""

        row = await self._session.get(self.model, id_)
        if row is None:
            return None
        return self._to_entity(row)

    async def get_by_id(self, id_: uuid.UUID) -> EntityT:
        """Busca por ID, levantando `NotFoundError` quando não existe."""

        entity = await self.get_by_id_or_none(id_)
        if entity is None:
            raise NotFoundError(f"Registro com ID {id_} não encontrado.")
        return entity

    async def create(self, create_command: BaseCreateCommand) -> EntityT:
        """Insere um registro a partir do comando de criação."""

        obj = self.model(**create_command.to_dict())
        self._session.add(obj)
        # O flush materializa o INSERT (e os defaults do servidor) ainda dentro
        # da transação, para que a entidade devolvida já tenha id e timestamps.
        await self._session.flush()
        await self._session.refresh(obj)
        return self._to_entity(obj)

    async def update(
        self,
        id_: uuid.UUID,
        update_command: BaseUpdateCommand,
    ) -> EntityT:
        """Atualiza só os campos informados no comando (os não-`UNSET`)."""

        obj = await self._get_model_by_id(id_)
        for field, value in update_command.defined_values().items():
            setattr(obj, field, value)
        await self._session.flush()
        await self._session.refresh(obj)
        return self._to_entity(obj)

    async def delete(self, id_: uuid.UUID) -> None:
        """Remove um registro pelo ID."""

        stmt = sa.delete(self.model).where(self.model.id == id_)  # type: ignore[attr-defined]
        # `execute` promete um `Result` genérico; só o `CursorResult` de um DML
        # carrega `rowcount`, que é como se distingue "apagou" de "não existia".
        result = cast(CursorResult[Any], await self._session.execute(stmt))
        if result.rowcount == 0:
            raise NotFoundError(f"Registro com ID {id_} não encontrado.")

    async def paginate(
        self,
        page_params: PageParams,
        filters: FiltersT | None = None,
    ) -> Page[EntityT]:
        """Lista uma página aplicando os filtros do módulo."""

        filters = filters or self.filters_type()
        stmt = self._apply_filters(sa.select(self.model), filters)
        return await self._paginate(stmt, page_params)

    async def _paginate(
        self, stmt: sa.Select[Any], params: PageParams
    ) -> Page[EntityT]:
        """Executa a contagem e a página de uma query já filtrada."""

        count_stmt = sa.select(sa.func.count()).select_from(
            stmt.order_by(None).subquery()
        )
        total = await self._session.scalar(count_stmt) or 0

        result = await self._session.execute(
            stmt.offset((params.page - 1) * params.page_size).limit(params.page_size)
        )
        rows = result.scalars().all()

        return Page(
            items=[self._to_entity(row) for row in rows],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    def _apply_filters(self, stmt: sa.Select[Any], filters: FiltersT) -> sa.Select[Any]:
        """Aplica os filtros do módulo. Por padrão, não filtra nada."""

        return stmt

    async def _get_model_or_none(self, id_: uuid.UUID) -> ModelT | None:
        """Busca a linha (não a entidade) por ID, ou `None`."""

        return await self._session.get(self.model, id_)

    async def _get_model_by_id(self, id_: uuid.UUID) -> ModelT:
        """Busca a linha (não a entidade) por ID, ou levanta `NotFoundError`."""

        obj = await self._get_model_or_none(id_)
        if obj is None:
            raise NotFoundError(f"Registro com ID {id_} não encontrado.")
        return obj
