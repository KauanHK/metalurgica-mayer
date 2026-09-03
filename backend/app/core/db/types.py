"""Tipos de coluna reaproveitados pelos models.

Centralizados para que "dinheiro", "quantidade" e "chave primária" tenham a
mesma definição em todas as tabelas — divergir a precisão de um `Numeric` entre
o item do orçamento e o total é como um centavo aparece do nada no fechamento.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from sqlalchemy import DateTime, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column

# Chave primária: UUIDv7 é ordenável no tempo, então o índice não fragmenta como
# faria com UUIDv4 — e continua sem revelar contagem de registros, como um
# inteiro sequencial revelaria.
UuidPk = Annotated[
    uuid.UUID,
    mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid7),
]

# Valores monetários: 14 dígitos com 2 casas. Nunca float — 0.1 + 0.2 em binário
# não fecha caixa.
Money = Annotated[Decimal, mapped_column(Numeric(14, 2))]

# Quantidades de estoque: 3 casas decimais cobrem o material vendido por metro
# ou por quilo, sem obrigar o cadastro a arredondar.
Quantity = Annotated[Decimal, mapped_column(Numeric(14, 3))]

CreatedAt = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False),
]

UpdatedAt = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    ),
]
