from enum import StrEnum


class MaterialUnit(StrEnum):
    """Unidade em que o material é medido e movimentado."""

    UNIT = "unit"
    """Unidade (peças, parafusos, conexões)."""

    KILOGRAM = "kg"
    """Quilograma (chapas, perfis vendidos por peso)."""

    METER = "m"
    """Metro linear (barras, tubos, cantoneiras)."""

    SQUARE_METER = "m2"
    """Metro quadrado (chapas por área)."""

    LITER = "l"
    """Litro (tintas, solventes, fluidos)."""


class StockMovementType(StrEnum):
    """Sentido da movimentação de estoque.

    O sinal da quantidade vem daqui, e não do número gravado: a coluna
    `quantity` é sempre positiva (há um CHECK), o que impede uma entrada
    negativa de virar uma saída silenciosa e desfazer a conta do saldo.
    """

    INBOUND = "inbound"
    """Entrada: compra, devolução, sobra que volta ao estoque."""

    OUTBOUND = "outbound"
    """Saída: consumo em produção, perda, descarte."""
