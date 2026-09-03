from enum import StrEnum


class AssetCondition(StrEnum):
    """Estado de conservação do bem."""

    NEW = "new"
    """Novo: sem uso ou recém-adquirido."""

    GOOD = "good"
    """Bom: em uso, sem restrições."""

    FAIR = "fair"
    """Regular: desgaste visível, ainda operante."""

    POOR = "poor"
    """Ruim: precisa de reparo ou substituição."""


class AssetStatus(StrEnum):
    """Situação do bem na operação.

    Separada da conservação de propósito: um bem em bom estado pode estar parado
    por falta de demanda, e um em estado ruim pode seguir em operação. Juntar as
    duas coisas numa coluna só perderia essa distinção.
    """

    ACTIVE = "active"
    """Ativo: em uso."""

    MAINTENANCE = "maintenance"
    """Em manutenção: fora de operação temporariamente."""

    INACTIVE = "inactive"
    """Inativo: baixado, vendido ou encostado."""
