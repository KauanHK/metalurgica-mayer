from enum import StrEnum


class QuoteStatus(StrEnum):
    """Situação do orçamento perante o cliente."""

    PENDING = "pending"
    """Pendente: enviado, aguardando resposta."""

    APPROVED = "approved"
    """Aprovado: o cliente aceitou e o serviço pode ser executado."""

    REJECTED = "rejected"
    """Recusado: o cliente não aceitou."""
