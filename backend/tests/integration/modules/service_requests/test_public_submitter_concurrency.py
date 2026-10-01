"""Corrida entre dois envios do mesmo documento novo no `PublicServiceRequestSubmitter`.

Não dá para provocar a corrida de verdade na transação única dos testes de
integração; um UoW falso reproduz o efeito: a primeira tentativa esbarra na
unicidade do documento, e a segunda já encontra o cliente do outro envio.
"""

import uuid
from datetime import UTC, datetime
from types import TracebackType
from typing import Self

import pytest
from sqlalchemy.exc import IntegrityError

from app.modules.clients.domain.entities import Client, NewClient
from app.modules.service_requests.application.dtos.commands import (
    SubmitPublicServiceRequestCommand,
)
from app.modules.service_requests.application.use_cases.public_service_request_submitter import (  # noqa: E501
    PublicServiceRequestSubmitter,
)
from app.modules.service_requests.domain.entities import (
    NewServiceRequest,
    ServiceRequest,
)

DOCUMENT = "52998224725"
NOW = datetime(2026, 10, 1, tzinfo=UTC)


def make_client() -> Client:
    return Client(
        id=uuid.uuid4(),
        name="Maria",
        document=DOCUMENT,
        phone=None,
        email=None,
        zip_code=None,
        street=None,
        number=None,
        complement=None,
        neighborhood=None,
        city=None,
        state=None,
        notes=None,
        is_active=True,
        created_at=NOW,
        updated_at=NOW,
    )


class FakeClients:
    """Na 1ª tentativa não acha o cliente e falha ao criar; na 2ª já o acha."""

    def __init__(self, existing: Client, attempts: list[int]) -> None:
        self._existing = existing
        self._attempts = attempts

    async def get_by_id_or_none(self, id_: uuid.UUID) -> Client | None:
        return None

    async def get_by_document_or_none(self, document: str) -> Client | None:
        return self._existing if len(self._attempts) > 1 else None

    async def get_by_email_or_none(self, email: str) -> Client | None:
        return None

    async def create(self, create_command: NewClient) -> Client:
        raise IntegrityError("INSERT INTO clients", {}, Exception("duplicate"))


class FakeServiceRequests:
    def __init__(self) -> None:
        self.created: list[NewServiceRequest] = []

    async def create(self, create_command: NewServiceRequest) -> ServiceRequest:
        self.created.append(create_command)
        return ServiceRequest(
            id=uuid.uuid4(),
            client_id=create_command.client_id,
            client_name="Maria",
            title=create_command.title,
            description=create_command.description,
            status=create_command.status,
            origin=create_command.origin,
            requested_at=create_command.requested_at,
            due_date=create_command.due_date,
            created_at=NOW,
            updated_at=NOW,
        )


class FakeUnitOfWork:
    def __init__(self, existing: Client) -> None:
        self.attempts: list[int] = []
        self.service_requests = FakeServiceRequests()
        self.clients = FakeClients(existing, self.attempts)

    async def __aenter__(self) -> Self:
        self.attempts.append(1)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        return None


def command() -> SubmitPublicServiceRequestCommand:
    return SubmitPublicServiceRequestCommand(
        name="Maria",
        title="Portão",
        description="Portão de garagem",
        email="m@a.com",
        document=DOCUMENT,
    )


async def test_tenta_de_novo_e_reaproveita_o_cliente_da_corrida() -> None:
    existing = make_client()
    uow = FakeUnitOfWork(existing)

    result = await PublicServiceRequestSubmitter(uow=uow).submit(command())  # type: ignore[arg-type]

    assert len(uow.attempts) == 2
    assert result.client_id == existing.id


async def test_segunda_falha_de_integridade_e_propagada() -> None:
    class AlwaysMissing(FakeClients):
        async def get_by_document_or_none(self, document: str) -> Client | None:
            return None

    uow = FakeUnitOfWork(make_client())
    uow.clients = AlwaysMissing(make_client(), uow.attempts)

    with pytest.raises(IntegrityError):
        await PublicServiceRequestSubmitter(uow=uow).submit(command())  # type: ignore[arg-type]

    assert len(uow.attempts) == 2
