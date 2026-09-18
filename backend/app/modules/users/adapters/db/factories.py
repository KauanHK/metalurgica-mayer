from app.core.db.session import db
from app.modules.users.adapters.db.unit_of_work import UsersUnitOfWork


def make_unit_of_work() -> UsersUnitOfWork:
    """Fábrica do UoW de usuários.

    É esta função que o FastAPI injeta — e é ela que os testes sobrescrevem por
    `app.dependency_overrides`, trocando o engine global pela sessão presa à
    transação do teste.
    """

    return UsersUnitOfWork(session_factory=db.create_session)
