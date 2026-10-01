import uuid
from dataclasses import dataclass
from datetime import date

from app.modules.service_requests.domain.entities import (
    ServiceRequestOrigin,
    ServiceRequestStatus,
)


@dataclass(frozen=True, slots=True)
class ServiceRequestFilters:
    """Filtros da listagem de solicitações."""

    client_id: uuid.UUID | None = None
    status: ServiceRequestStatus | None = None

    origin: ServiceRequestOrigin | None = None
    """Por onde entrou; é o filtro de triagem dos pedidos vindos do site."""

    date_from: date | None = None
    """Início do período (inclusivo), sobre `requested_at`."""

    date_to: date | None = None
    """Fim do período (inclusivo), sobre `requested_at`."""

    search: str | None = None
    """Busca livre por trecho do título."""
