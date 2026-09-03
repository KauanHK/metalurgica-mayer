import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from app.core.types import UNSET, BaseCreateCommand, BaseUpdateCommand, Unset


@dataclass(frozen=True, slots=True)
class NewClient(BaseCreateCommand):
    """Dados de um cliente a ser inserido, já normalizados."""

    name: str
    document: str | None
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


@dataclass(frozen=True, slots=True)
class UpdateClient(BaseUpdateCommand):
    """Campos a alterar num cliente. `UNSET` = não mexer."""

    name: str | Unset = UNSET
    document: str | Unset | None = UNSET
    phone: str | Unset | None = UNSET
    email: str | Unset | None = UNSET
    zip_code: str | Unset | None = UNSET
    street: str | Unset | None = UNSET
    number: str | Unset | None = UNSET
    complement: str | Unset | None = UNSET
    neighborhood: str | Unset | None = UNSET
    city: str | Unset | None = UNSET
    state: str | Unset | None = UNSET
    notes: str | Unset | None = UNSET
    is_active: bool | Unset = UNSET


@dataclass(frozen=True, slots=True)
class Client:
    """Cliente da metalúrgica."""

    id: uuid.UUID
    name: str
    document: str | None
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

    @property
    def document_type(self) -> Literal["CPF", "CNPJ"] | None:
        """Deduz o tipo do documento pelo número de dígitos."""

        if self.document is None:
            return None
        return "CPF" if len(self.document) == 11 else "CNPJ"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "document": self.document,
            "document_type": self.document_type,
            "phone": self.phone,
            "email": self.email,
            "zip_code": self.zip_code,
            "street": self.street,
            "number": self.number,
            "complement": self.complement,
            "neighborhood": self.neighborhood,
            "city": self.city,
            "state": self.state,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
