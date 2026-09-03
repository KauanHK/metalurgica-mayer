import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import Base
from app.core.db.types import CreatedAt, Money, Quantity, UpdatedAt, UuidPk
from app.modules.quotes.domain.entities import QuoteStatus


class Quote(Base):
    """Orçamento emitido para uma solicitação (Sprint 5)."""

    __tablename__ = "quotes"

    id: Mapped[UuidPk]
    service_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("service_requests.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[QuoteStatus] = mapped_column(
        Enum(QuoteStatus, native_enum=False, length=20, validate_strings=True),
        default=QuoteStatus.PENDING,
        nullable=False,
    )
    # Total materializado, e não calculado na leitura: é o valor que o cliente
    # recebeu. Recalculá-lo pela soma dos itens faria um orçamento já aprovado
    # mudar de valor caso a tabela de preços ou um item fosse corrigido depois.
    # Quem o mantém em dia é o use case que grava os itens (Sprint 5).
    total_amount: Mapped[Money] = mapped_column(default=Decimal("0.00"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    issued_at: Mapped[date] = mapped_column(Date, nullable=False)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]

    __table_args__ = (
        Index("ix_quotes_service_request", "service_request_id"),
        Index("ix_quotes_status", "status"),
        CheckConstraint("total_amount >= 0", name="ck_quotes_total_nonnegative"),
    )


class QuoteItem(Base):
    """Linha de um orçamento: o que foi cotado, quanto e por qual preço."""

    __tablename__ = "quote_items"

    id: Mapped[UuidPk]
    quote_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        # CASCADE aqui, ao contrário das outras FKs: um item não tem existência
        # própria fora do orçamento que o contém.
        ForeignKey("quotes.id", ondelete="CASCADE"),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Quantity] = mapped_column(nullable=False)
    unit_price: Mapped[Money] = mapped_column(nullable=False)
    # Ordem de exibição, definida pelo usuário — a ordem de inserção não
    # sobrevive a uma edição que remova e recrie linhas.
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]

    __table_args__ = (
        Index("ix_quote_items_quote", "quote_id"),
        CheckConstraint("quantity > 0", name="ck_quote_items_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="ck_quote_items_price_nonnegative"),
    )
