import uuid
from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from typing import Any

from app.core.types import UNSET, BaseCreateCommand, BaseUpdateCommand, Unset


class ServiceRequestStatus(StrEnum):
    """Andamento da solicitação, do pedido à conclusão."""

    OPEN = "open"
    """Aberta: registrada, ainda não avaliada."""

    IN_ANALYSIS = "in_analysis"
    """Em análise: a equipe está orçando ou avaliando a viabilidade."""

    IN_PROGRESS = "in_progress"
    """Em execução: o serviço está sendo produzido."""

    COMPLETED = "completed"
    """Concluída: serviço entregue."""

    CANCELLED = "cancelled"
    """Cancelada: não será executada."""


class ServiceRequestOrigin(StrEnum):
    """Por onde a solicitação entrou.

    Distinguir a origem é o que permite, na Sprint 4, saber quais pedidos vieram
    do formulário público — eles chegam sem ninguém do lado de dentro conferindo
    e podem precisar de triagem.
    """

    INTERNAL = "internal"
    """Cadastrada por um usuário do ERP."""

    WEBSITE = "website"
    """Enviada pelo formulário do site institucional."""


# Estados dos quais a solicitação não sai mais: o serviço foi entregue ou a
# demanda foi encerrada. Reabrir seria reescrever o histórico — para um novo
# pedido, cadastra-se uma nova solicitação.
TERMINAL_STATUSES: frozenset[ServiceRequestStatus] = frozenset(
    {ServiceRequestStatus.COMPLETED, ServiceRequestStatus.CANCELLED}
)


@dataclass(frozen=True, slots=True)
class NewServiceRequest(BaseCreateCommand):
    """Dados de uma solicitação a ser inserida, já normalizados."""

    client_id: uuid.UUID
    title: str
    description: str | None
    status: ServiceRequestStatus
    origin: ServiceRequestOrigin
    requested_at: date
    due_date: date | None


@dataclass(frozen=True, slots=True)
class UpdateServiceRequest(BaseUpdateCommand):
    """Campos a alterar numa solicitação. `UNSET` = não mexer.

    O cliente não está aqui de propósito: a solicitação pertence ao cliente que
    a fez e não muda de dono.
    """

    title: str | Unset = UNSET
    description: str | Unset | None = UNSET
    status: ServiceRequestStatus | Unset = UNSET
    requested_at: date | Unset = UNSET
    due_date: date | Unset | None = UNSET


@dataclass(frozen=True, slots=True)
class ServiceRequest:
    """Solicitação de serviço feita por um cliente."""

    id: uuid.UUID
    client_id: uuid.UUID
    client_name: str
    title: str
    description: str | None
    status: ServiceRequestStatus
    origin: ServiceRequestOrigin
    requested_at: date
    due_date: date | None
    created_at: datetime
    updated_at: datetime

    @property
    def is_terminal(self) -> bool:
        """Indica se a solicitação já foi concluída ou cancelada."""

        return self.status in TERMINAL_STATUSES

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "client_id": self.client_id,
            "client_name": self.client_name,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "origin": self.origin,
            "requested_at": self.requested_at,
            "due_date": self.due_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
