from app.core.db.session import db
from app.modules.clients.adapters.db.unit_of_work import ClientsUnitOfWork


def make_unit_of_work() -> ClientsUnitOfWork:
    """Fábrica do UoW de clientes.

    É esta função que o FastAPI injeta — e é ela que os testes sobrescrevem por
    `app.dependency_overrides`, trocando o engine global pela sessão presa à
    transação do teste.
    """

    return ClientsUnitOfWork(session_factory=db.create_session)
