from dataclasses import dataclass

from app.core.types import UNSET, BaseCreateCommand, BaseUpdateCommand, Unset


@dataclass(frozen=True, slots=True)
class CreateClientCommand(BaseCreateCommand):
    """Entrada do `ClientsCreator`."""

    name: str
    document: str | None = None
    phone: str | None = None
    email: str | None = None
    zip_code: str | None = None
    street: str | None = None
    number: str | None = None
    complement: str | None = None
    neighborhood: str | None = None
    city: str | None = None
    state: str | None = None
    notes: str | None = None
    is_active: bool = True


@dataclass(frozen=True, slots=True)
class UpdateClientCommand(BaseUpdateCommand):
    """Entrada do `ClientsUpdater`. Campos ausentes ficam `UNSET`."""

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
