from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ClientFilters:
    """Filtros da listagem de clientes."""

    search: str | None = None
    """Busca livre por nome, documento, e-mail ou telefone."""

    is_active: bool | None = None
    """`None` traz ativos e inativos."""
