from typing import Any

import sqlalchemy as sa

from app.core.db.repository import BaseRepository
from app.modules.clients.adapters.db.models import Client as ClientModel
from app.modules.clients.application.dtos.filters import ClientFilters
from app.modules.clients.domain.entities import Client


class ClientsRepository(BaseRepository[ClientModel, Client, ClientFilters]):
    model = ClientModel
    filters_type = ClientFilters

    def _to_entity(self, row: ClientModel) -> Client:
        return Client(
            id=row.id,
            name=row.name,
            document=row.document,
            phone=row.phone,
            email=row.email,
            zip_code=row.zip_code,
            street=row.street,
            number=row.number,
            complement=row.complement,
            neighborhood=row.neighborhood,
            city=row.city,
            state=row.state,
            notes=row.notes,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def _apply_filters(
        self, stmt: sa.Select[Any], filters: ClientFilters
    ) -> sa.Select[Any]:
        if filters.search:
            pattern = f"%{filters.search.strip()}%"
            stmt = stmt.where(
                sa.or_(
                    ClientModel.name.ilike(pattern),
                    ClientModel.document.ilike(pattern),
                    ClientModel.email.ilike(pattern),
                    ClientModel.phone.ilike(pattern),
                )
            )
        if filters.is_active is not None:
            stmt = stmt.where(ClientModel.is_active == filters.is_active)
        # Ordem estável na listagem: sem ela, duas páginas seguidas podem repetir
        # ou pular um cliente, porque o Postgres não promete ordem sem ORDER BY.
        return stmt.order_by(ClientModel.name.asc(), ClientModel.id.asc())

    async def get_by_document_or_none(self, document: str) -> Client | None:
        """Busca pelo documento (CPF/CNPJ), que é único quando informado."""

        result = await self._session.execute(
            sa.select(self.model).where(self.model.document == document)
        )
        row = result.scalars().one_or_none()
        return self._to_entity(row) if row else None
