import uuid
from dataclasses import dataclass
from datetime import date

from app.core.types import UNSET, BaseCreateCommand, BaseUpdateCommand, Unset
from app.modules.service_requests.domain.entities import ServiceRequestStatus


@dataclass(frozen=True, slots=True)
class CreateServiceRequestCommand(BaseCreateCommand):
    """Entrada do `ServiceRequestsCreator`."""

    client_id: uuid.UUID
    title: str
    description: str | None = None
    requested_at: date | None = None
    """`None` = hoje, no fuso da operação."""

    due_date: date | None = None


@dataclass(frozen=True, slots=True)
class UpdateServiceRequestCommand(BaseUpdateCommand):
    """Entrada do `ServiceRequestsUpdater`. Campos ausentes ficam `UNSET`."""

    title: str | Unset = UNSET
    description: str | Unset | None = UNSET
    status: ServiceRequestStatus | Unset = UNSET
    requested_at: date | Unset = UNSET
    due_date: date | Unset | None = UNSET


@dataclass(frozen=True, slots=True)
class SubmitPublicServiceRequestCommand(BaseCreateCommand):
    """Entrada do `PublicServiceRequestSubmitter`: o que o formulário do site traz.

    Os dados do solicitante vêm de fora do sistema e não são confiáveis: servem
    para encontrar (ou cadastrar) o cliente, nunca para alterar um existente.
    """

    name: str
    title: str
    description: str
    email: str | None = None
    phone: str | None = None
    document: str | None = None
