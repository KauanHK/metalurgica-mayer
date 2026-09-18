from dataclasses import dataclass

from app.core.types import UNSET, BaseUpdateCommand, Unset


@dataclass(frozen=True, slots=True)
class UpdateProfileCommand(BaseUpdateCommand):
    """Entrada do `UsersUpdater` — edição do próprio perfil."""

    name: str | Unset = UNSET
    phone: str | Unset | None = UNSET


@dataclass(frozen=True, slots=True)
class ChangePasswordCommand:
    """Entrada do `PasswordChanger`.

    Não estende `BaseUpdateCommand`: é uma ação (trocar a senha mediante a
    senha atual), não uma edição parcial de campos da entidade.
    """

    current_password: str
    new_password: str
