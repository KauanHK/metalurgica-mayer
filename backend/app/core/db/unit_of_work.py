import logging
from collections.abc import Callable
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class BaseUnitOfWork:
    """Transação como context manager: commit ao sair limpo, rollback na exceção.

    Recebe uma *fábrica* de sessões, e não uma sessão: assim o mesmo UoW pode ser
    reutilizado e, nos testes, a fábrica é trocada por uma presa à transação do
    teste (ver `tests/integration/conftest.py`).

    Os UoW de cada módulo herdam daqui e expõem seus repositórios como
    propriedades, instanciadas no `__aenter__` sobre a sessão da transação.
    """

    def __init__(self, session_factory: Callable[[], AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession:
        """Sessão da transação em curso."""

        if self._session is None:
            raise RuntimeError(
                "Sessão não inicializada: use o UnitOfWork como context manager "
                "(`async with uow as uow: ...`)."
            )
        return self._session

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        try:
            if exc_type is None:
                await self._handle_commit()
            else:
                await self._handle_rollback()
        finally:
            await self.session.close()
            self._session = None

    async def _handle_commit(self) -> None:
        """Commita a transação; em falha, faz rollback e propaga."""

        try:
            await self.session.commit()
        except Exception:
            logger.error("Erro ao commitar a transação.", exc_info=True)
            await self._handle_rollback()
            raise

    async def _handle_rollback(self) -> None:
        """Faz rollback da transação, registrando falha sem mascarar a original."""

        try:
            await self.session.rollback()
        except Exception:
            logger.error("Erro ao fazer rollback da transação.", exc_info=True)
