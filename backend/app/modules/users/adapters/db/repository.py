import uuid

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.modules.users.adapters.db.models import User as UserModel
from app.modules.users.domain.entities import UpdateUser, User, UserCredentials


class UsersRepository:
    """Repositório de usuários.

    Não estende `BaseRepository`: nesta parte da Sprint 2 o módulo só precisa
    de busca por id/e-mail e atualização pontual do próprio perfil. O CRUD
    genérico (com paginação) só se justifica quando o cadastro de usuários por
    um admin for implementado — aí sim vale herdar, como `ClientsRepository`.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, row: UserModel) -> User:
        return User(
            id=row.id,
            name=row.name,
            email=row.email,
            phone=row.phone,
            role=row.role,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    async def _get_model_by_id(self, id_: uuid.UUID) -> UserModel:
        obj = await self._session.get(UserModel, id_)
        if obj is None:
            raise NotFoundError(f"Usuário com ID {id_} não encontrado.")
        return obj

    async def get_by_id_or_none(self, id_: uuid.UUID) -> User | None:
        row = await self._session.get(UserModel, id_)
        return self._to_entity(row) if row is not None else None

    async def get_by_id(self, id_: uuid.UUID) -> User:
        return self._to_entity(await self._get_model_by_id(id_))

    async def get_credentials_by_id(self, id_: uuid.UUID) -> UserCredentials:
        row = await self._get_model_by_id(id_)
        return UserCredentials(
            user=self._to_entity(row), password_hash=row.password_hash
        )

    async def get_credentials_by_email(self, email: str) -> UserCredentials | None:
        result = await self._session.execute(
            sa.select(UserModel).where(UserModel.email == email)
        )
        row = result.scalars().one_or_none()
        if row is None:
            return None
        return UserCredentials(
            user=self._to_entity(row), password_hash=row.password_hash
        )

    async def update(self, id_: uuid.UUID, update_command: UpdateUser) -> User:
        obj = await self._get_model_by_id(id_)
        for field, value in update_command.defined_values().items():
            setattr(obj, field, value)
        await self._session.flush()
        await self._session.refresh(obj)
        return self._to_entity(obj)

    async def set_password_hash(self, id_: uuid.UUID, password_hash: str) -> None:
        obj = await self._get_model_by_id(id_)
        obj.password_hash = password_hash
        await self._session.flush()
