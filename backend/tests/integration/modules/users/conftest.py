"""Fixtures dos testes do módulo `users`.

Insere usuários direto pelo model SQLAlchemy — como o seed do admin inicial —,
porque esta parte da Sprint 2 ainda não expõe um endpoint de cadastro.
"""

from collections.abc import Callable

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.actors.roles import UserRole
from app.core.security.passwords import hash_password
from app.modules.users.adapters.db.models import User as UserModel

PASSWORD = "senha-forte-123"


async def _create_user(
    session_factory: Callable[[], AsyncSession], *, email: str, is_active: bool
) -> UserModel:
    session = session_factory()
    user = UserModel(
        name="Usuária de Teste",
        email=email,
        phone=None,
        password_hash=hash_password(PASSWORD),
        role=UserRole.OPERATOR,
        is_active=is_active,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def existing_user(session_factory: Callable[[], AsyncSession]) -> UserModel:
    """Usuário ativo, com a senha em `PASSWORD`."""

    return await _create_user(
        session_factory, email="usuaria@metalurgicamayer.com.br", is_active=True
    )


@pytest_asyncio.fixture
async def inactive_user(session_factory: Callable[[], AsyncSession]) -> UserModel:
    """Usuário desativado, com a senha em `PASSWORD`."""

    return await _create_user(
        session_factory, email="inativa@metalurgicamayer.com.br", is_active=False
    )
