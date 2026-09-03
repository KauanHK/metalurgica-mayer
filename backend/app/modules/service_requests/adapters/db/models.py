import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import Base
from app.core.db.types import CreatedAt, UpdatedAt, UuidPk
from app.modules.service_requests.domain.entities import (
    ServiceRequestOrigin,
    ServiceRequestStatus,
)


class ServiceRequest(Base):
    """Solicitação de serviço feita por um cliente (Sprint 4)."""

    __tablename__ = "service_requests"

    id: Mapped[UuidPk]
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        # RESTRICT: excluir um cliente que tem histórico apagaria o registro do
        # que foi feito para ele. Quem sai de cena é desativado (`is_active`),
        # não removido.
        ForeignKey("clients.id", ondelete="RESTRICT"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ServiceRequestStatus] = mapped_column(
        Enum(ServiceRequestStatus, native_enum=False, length=20, validate_strings=True),
        default=ServiceRequestStatus.OPEN,
        nullable=False,
    )
    origin: Mapped[ServiceRequestOrigin] = mapped_column(
        Enum(ServiceRequestOrigin, native_enum=False, length=20, validate_strings=True),
        default=ServiceRequestOrigin.INTERNAL,
        nullable=False,
    )
    requested_at: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]

    __table_args__ = (
        # A ficha do cliente lista as solicitações dele da mais recente para a
        # mais antiga; o índice composto cobre exatamente essa consulta.
        Index("ix_service_requests_client_requested", "client_id", "requested_at"),
        Index("ix_service_requests_status", "status"),
    )
