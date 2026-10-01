from app.core.db.session import db
from app.modules.service_requests.adapters.db.unit_of_work import (
    ServiceRequestsUnitOfWork,
)


def make_unit_of_work() -> ServiceRequestsUnitOfWork:
    """Fábrica do UoW de solicitações.

    É esta função que o FastAPI injeta — e é ela que os testes sobrescrevem por
    `app.dependency_overrides`, trocando o engine global pela sessão presa à
    transação do teste.
    """

    return ServiceRequestsUnitOfWork(session_factory=db.create_session)
