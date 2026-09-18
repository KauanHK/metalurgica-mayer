from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.actors.roles import UserRole
from app.core.db.base import Base
from app.core.db.types import CreatedAt, UpdatedAt, UuidPk


class User(Base):
    """Usuário do ERP."""

    __tablename__ = "users"

    id: Mapped[UuidPk]
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        # `native_enum=False` grava VARCHAR + CHECK em vez de um tipo ENUM do
        # Postgres. Acrescentar um perfil vira uma alteração de constraint, e não
        # um `ALTER TYPE` — que no Postgres não roda dentro de transação e por
        # isso atravessa mal uma migration.
        Enum(UserRole, native_enum=False, length=20, validate_strings=True),
        default=UserRole.OPERATOR,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
