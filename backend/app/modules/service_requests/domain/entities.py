from enum import StrEnum


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
