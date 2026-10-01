"""Testes do `ClientsRepository` que dependem do banco de verdade."""

from collections.abc import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.clients.adapters.db.repository import ClientsRepository
from app.modules.clients.domain.entities import NewClient


def new_client(name: str, email: str | None, *, is_active: bool = True) -> NewClient:
    return NewClient(
        name=name,
        document=None,
        phone=None,
        email=email,
        zip_code=None,
        street=None,
        number=None,
        complement=None,
        neighborhood=None,
        city=None,
        state=None,
        notes=None,
        is_active=is_active,
    )


class TestGetByEmailOrNone:
    async def test_acha_sem_diferenciar_maiusculas_de_minusculas(
        self, session_factory: Callable[[], AsyncSession]
    ) -> None:
        repo = ClientsRepository(session_factory())
        criado = await repo.create(new_client("Silva", "Contato@Silva.com.br"))

        assert (await repo.get_by_email_or_none("contato@silva.com.br")) == criado
        assert (await repo.get_by_email_or_none("  CONTATO@SILVA.COM.BR ")) == criado

    async def test_devolve_none_quando_nao_existe(
        self, session_factory: Callable[[], AsyncSession]
    ) -> None:
        repo = ClientsRepository(session_factory())
        await repo.create(new_client("Silva", "contato@silva.com.br"))

        assert await repo.get_by_email_or_none("outro@silva.com.br") is None

    async def test_curingas_do_like_nao_casam_com_nada(
        self, session_factory: Callable[[], AsyncSession]
    ) -> None:
        repo = ClientsRepository(session_factory())
        await repo.create(new_client("Silva", "contato@silva.com.br"))

        assert await repo.get_by_email_or_none("%@silva.com.br") is None
        assert await repo.get_by_email_or_none("c_ntato@silva.com.br") is None

    async def test_com_varios_prefere_o_ativo_e_depois_o_mais_antigo(
        self, session_factory: Callable[[], AsyncSession]
    ) -> None:
        repo = ClientsRepository(session_factory())
        await repo.create(new_client("Inativo antigo", "dup@x.com", is_active=False))
        ativo_antigo = await repo.create(new_client("Ativo antigo", "dup@x.com"))
        await repo.create(new_client("Ativo novo", "DUP@x.com"))

        achado = await repo.get_by_email_or_none("dup@x.com")

        assert achado is not None
        assert achado.id == ativo_antigo.id
