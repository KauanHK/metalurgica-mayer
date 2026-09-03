from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.validators import validate_cpf_or_cnpj

Name = Annotated[str, Field(min_length=2, max_length=150)]
Document = Annotated[str, Field(max_length=18)]
Phone = Annotated[str, Field(max_length=20)]
ZipCode = Annotated[str, Field(pattern=r"^\d{8}$")]
State = Annotated[str, Field(pattern=r"^[A-Za-z]{2}$")]


def _normalize_document(value: str | None) -> str | None:
    """Valida o CPF/CNPJ e guarda só os dígitos.

    A máscara é assunto da tela: normalizar na entrada é o que torna a busca e a
    constraint de unicidade confiáveis — sem isso, "12.345.678/0001-90" e
    "12345678000190" seriam dois clientes diferentes.
    """

    if value is None or not value.strip():
        return None
    return validate_cpf_or_cnpj(value)


def _blank_to_none(value: str | None) -> str | None:
    """Trata string vazia como ausência.

    Um formulário HTML manda `""` para todo campo opcional não preenchido;
    gravar isso encheria o banco de vazios que não são nulos e quebraria a
    unicidade do documento na segunda vez.
    """

    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


class ClientBase(BaseModel):
    """Campos comuns à criação e à edição."""

    name: Name
    document: Document | None = None
    phone: Phone | None = None
    email: EmailStr | None = None
    zip_code: ZipCode | None = None
    street: Annotated[str | None, Field(max_length=255)] = None
    number: Annotated[str | None, Field(max_length=20)] = None
    complement: Annotated[str | None, Field(max_length=150)] = None
    neighborhood: Annotated[str | None, Field(max_length=100)] = None
    city: Annotated[str | None, Field(max_length=100)] = None
    state: State | None = None
    notes: str | None = None

    @field_validator("document", mode="before")
    @classmethod
    def _check_document(cls, value: str | None) -> str | None:
        return _normalize_document(value)

    @field_validator(
        "phone",
        "street",
        "number",
        "complement",
        "neighborhood",
        "city",
        "notes",
        mode="before",
    )
    @classmethod
    def _empty_to_none(cls, value: str | None) -> str | None:
        return _blank_to_none(value)

    @field_validator("state", mode="after")
    @classmethod
    def _upper_state(cls, value: str | None) -> str | None:
        return value.upper() if value else None


class ClientCreate(ClientBase):
    """Corpo do `POST /clients`."""

    is_active: bool = True


class ClientUpdate(ClientBase):
    """Corpo do `PATCH /clients/{id}`.

    Todos os campos são opcionais — inclusive `name`, que é obrigatório na
    criação. O que não vier no corpo não é tocado (`exclude_unset` no router).
    """

    name: Name | None = None  # type: ignore[assignment]
    is_active: bool | None = None


class ClientRead(BaseModel):
    """Cliente como a API o devolve."""

    id: UUID
    name: str
    document: str | None
    document_type: Literal["CPF", "CNPJ"] | None
    phone: str | None
    email: str | None
    zip_code: str | None
    street: str | None
    number: str | None
    complement: str | None
    neighborhood: str | None
    city: str | None
    state: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClientsPaginationFilters(BaseModel):
    """Query params da listagem de clientes."""

    search: Annotated[str | None, Field(max_length=150)] = None
    is_active: bool | None = None
