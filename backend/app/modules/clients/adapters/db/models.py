from sqlalchemy import Boolean, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import Base
from app.core.db.types import CreatedAt, UpdatedAt, UuidPk


class Client(Base):
    """Cliente da metalúrgica — o CRUD-piloto da Sprint 1, módulo real da 3."""

    __tablename__ = "clients"

    id: Mapped[UuidPk]
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    # CPF (11) ou CNPJ (14), só dígitos — a máscara é assunto da tela. Opcional
    # porque a empresa atende quem chega, e o documento nem sempre vem no
    # primeiro contato; único quando informado (no Postgres, vários NULL não
    # colidem numa constraint UNIQUE).
    document: Mapped[str | None] = mapped_column(String(14), unique=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    zip_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    street: Mapped[str | None] = mapped_column(String(255), nullable=True)
    number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    complement: Mapped[str | None] = mapped_column(String(150), nullable=True)
    neighborhood: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]

    __table_args__ = (
        # A listagem busca por nome e ordena por ele.
        Index("ix_clients_name", "name"),
    )
