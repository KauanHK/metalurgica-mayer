from datetime import date, datetime
from typing import Annotated, Self
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.core.validators import validate_cpf_or_cnpj
from app.modules.clients.adapters.http.schemas import Document, Name, Phone
from app.modules.service_requests.domain.entities import (
    ServiceRequestOrigin,
    ServiceRequestStatus,
)

Title = Annotated[str, Field(min_length=3, max_length=150)]
DESCRIPTION_MAX_LENGTH = 5000


def _blank_to_none(value: str | None) -> str | None:
    """Trata string vazia como ausência (formulários mandam `""` em campo vazio)."""

    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


class ServiceRequestCreate(BaseModel):
    """Corpo do `POST /service-requests`."""

    client_id: UUID
    title: Title
    description: str | None = None
    requested_at: date | None = None
    """Omitido = hoje."""

    due_date: date | None = None

    @field_validator("title", mode="before")
    @classmethod
    def _strip_title(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("description", mode="before")
    @classmethod
    def _empty_to_none(cls, value: str | None) -> str | None:
        return _blank_to_none(value)


class PublicServiceRequestCreate(BaseModel):
    """Corpo do `POST /public/service-requests`, enviado pelo formulário do site.

    Reúne os dados do solicitante (mesmas regras do cadastro de clientes) e os
    do pedido. Pelo menos um meio de contato — e-mail ou telefone — é exigido,
    senão a equipe não teria como responder.
    """

    name: Name
    email: EmailStr | None = None
    phone: Phone | None = None
    document: Document | None = None
    """CPF ou CNPJ, com ou sem máscara; guardado só com os dígitos."""

    title: Title
    description: Annotated[str, Field(min_length=5, max_length=DESCRIPTION_MAX_LENGTH)]

    website: str | None = None
    """Honeypot: campo escondido no formulário, que gente não preenche.

    Se vier preenchido, é robô: a API responde 201 como se tivesse aceitado, mas
    não grava nada.
    """

    @field_validator("name", "title", "description", mode="before")
    @classmethod
    def _strip_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("document", mode="before")
    @classmethod
    def _check_document(cls, value: object) -> object:
        # Tipo errado (ex.: número no JSON) segue adiante e o Pydantic recusa.
        if not isinstance(value, str):
            return value
        return validate_cpf_or_cnpj(value) if value.strip() else None

    @field_validator("email", "phone", mode="before")
    @classmethod
    def _empty_to_none(cls, value: object) -> object:
        return _blank_to_none(value) if isinstance(value, str) else value

    @model_validator(mode="after")
    def _require_contact(self) -> Self:
        if self.email is None and self.phone is None:
            raise ValueError("Informe ao menos um contato: e-mail ou telefone.")
        return self

    @property
    def is_bot(self) -> bool:
        """Honeypot preenchido (ignorando espaços em branco)."""

        return bool(self.website and self.website.strip())


class PublicServiceRequestReceipt(BaseModel):
    """Comprovante do envio pelo site.

    Enxuto de propósito: o endpoint é público e não pode revelar se o e-mail ou
    o documento informado já pertence a um cliente.
    """

    id: UUID
    status: ServiceRequestStatus


class ServiceRequestUpdate(BaseModel):
    """Corpo do `PATCH /service-requests/{id}`.

    Todos os campos são opcionais; o que não vier no corpo não é tocado
    (`exclude_unset` no router). `description` e `due_date` aceitam `null` para
    limpar o valor; `title`, `status` e `requested_at` não.
    """

    title: Title | None = None
    description: str | None = None
    status: ServiceRequestStatus | None = None
    requested_at: date | None = None
    due_date: date | None = None

    @field_validator("title", mode="before")
    @classmethod
    def _strip_title(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("description", mode="before")
    @classmethod
    def _empty_to_none(cls, value: str | None) -> str | None:
        return _blank_to_none(value)

    @model_validator(mode="after")
    def _required_fields_not_null(self) -> Self:
        for field in ("title", "status", "requested_at"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"O campo {field} não pode ser nulo.")
        return self


class ServiceRequestRead(BaseModel):
    """Solicitação como a API a devolve."""

    id: UUID
    client_id: UUID
    client_name: str
    title: str
    description: str | None
    status: ServiceRequestStatus
    origin: ServiceRequestOrigin
    requested_at: date
    due_date: date | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClientServiceRequestsPaginationFilters(BaseModel):
    """Query params do histórico de um cliente (o cliente vem do caminho)."""

    status: ServiceRequestStatus | None = None
    origin: ServiceRequestOrigin | None = None
    date_from: date | None = None
    date_to: date | None = None
    search: Annotated[str | None, Field(max_length=150)] = None


class ServiceRequestsPaginationFilters(ClientServiceRequestsPaginationFilters):
    """Query params da listagem geral de solicitações."""

    client_id: UUID | None = None
