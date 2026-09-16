from datetime import date

from sqlalchemy import CheckConstraint, Date, Enum, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import Base
from app.core.db.types import CreatedAt, Money, UpdatedAt, UuidPk
from app.modules.assets.domain.entities import AssetCondition, AssetStatus


class Asset(Base):
    """Bem do patrimônio da empresa (Sprint 6)."""

    __tablename__ = "assets"

    id: Mapped[UuidPk]
    # Número de patrimônio, a plaquinha colada no bem. Opcional porque o cadastro
    # começa antes de a empresa etiquetar tudo; único quando informado.
    code: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    condition: Mapped[AssetCondition] = mapped_column(
        Enum(AssetCondition, native_enum=False, length=20, validate_strings=True),
        default=AssetCondition.GOOD,
        nullable=False,
    )
    status: Mapped[AssetStatus] = mapped_column(
        Enum(AssetStatus, native_enum=False, length=20, validate_strings=True),
        default=AssetStatus.ACTIVE,
        nullable=False,
    )
    location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    acquisition_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    acquisition_value: Mapped[Money | None] = mapped_column(nullable=True)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]

    __table_args__ = (
        Index("ix_assets_name", "name"),
        Index("ix_assets_status", "status"),
        CheckConstraint(
            "acquisition_value IS NULL OR acquisition_value >= 0",
            name="ck_assets_value_nonnegative",
        ),
    )
