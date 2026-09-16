import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import Base
from app.core.db.types import CreatedAt, Money, Quantity, UpdatedAt, UuidPk
from app.modules.inventory.domain.entities import MaterialUnit, StockMovementType


class Material(Base):
    """Material do almoxarifado (Sprint 5).

    **Não há coluna de saldo.** O saldo é a soma das entradas menos as saídas em
    `stock_movements`, calculada na consulta. Uma coluna materializada seria mais
    rápida e passaria a divergir das movimentações no primeiro registro corrigido
    ou excluído — e um almoxarifado que mente sobre o saldo é pior que um lento.
    Se o volume um dia justificar o cache, ele vem com o gatilho que o mantém.
    """

    __tablename__ = "materials"

    id: Mapped[UuidPk]
    code: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit: Mapped[MaterialUnit] = mapped_column(
        Enum(MaterialUnit, native_enum=False, length=20, validate_strings=True),
        nullable=False,
    )
    # Piso para o alerta de estoque baixo (escopo secundário da Sprint 5). Zero
    # significa "sem alerta configurado".
    minimum_stock: Mapped[Quantity] = mapped_column(
        default=Decimal("0.000"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]

    __table_args__ = (
        Index("ix_materials_name", "name"),
        CheckConstraint("minimum_stock >= 0", name="ck_materials_min_stock_nonneg"),
    )


class StockMovement(Base):
    """Entrada ou saída de material do estoque."""

    __tablename__ = "stock_movements"

    id: Mapped[UuidPk]
    material_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        # RESTRICT: apagar um material levaria junto o histórico que compõe o
        # saldo. Material que sai de linha é desativado.
        ForeignKey("materials.id", ondelete="RESTRICT"),
        nullable=False,
    )
    type: Mapped[StockMovementType] = mapped_column(
        Enum(StockMovementType, native_enum=False, length=20, validate_strings=True),
        nullable=False,
    )
    quantity: Mapped[Quantity] = mapped_column(nullable=False)
    unit_cost: Mapped[Money | None] = mapped_column(nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Quem registrou. SET NULL: excluir um usuário não pode apagar a
    # movimentação que ele lançou — o estoque perderia a conta.
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[CreatedAt]

    __table_args__ = (
        # O saldo é `SUM(...) WHERE material_id = ?`, e o extrato é a mesma
        # consulta ordenada por data: o índice composto serve às duas.
        Index("ix_stock_movements_material_occurred", "material_id", "occurred_at"),
        CheckConstraint("quantity > 0", name="ck_stock_movements_quantity_positive"),
        CheckConstraint(
            "unit_cost IS NULL OR unit_cost >= 0",
            name="ck_stock_movements_cost_nonnegative",
        ),
    )
