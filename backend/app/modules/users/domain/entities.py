import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.core.actors.roles import UserRole
from app.core.types import UNSET, BaseUpdateCommand, Unset

__all__ = ["UpdateUser", "User", "UserCredentials", "UserRole"]


@dataclass(frozen=True, slots=True)
class User:
    """Usuário do ERP.

    O hash da senha **não** faz parte da entidade: ele é detalhe de
    autenticação, e mantê-lo fora garante que nenhuma serialização distraída o
    devolva numa resposta. Quem precisa dele é o repositório, que o lê da linha.
    """

    id: uuid.UUID
    name: str
    email: str
    phone: str | None
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass(frozen=True, slots=True)
class UserCredentials:
    """Usuário mais o hash da senha.

    Existe separado de `User` porque só a autenticação e a troca de senha
    precisam do hash — devolvê-lo junto da entidade normal arriscaria uma
    serialização distraída vazá-lo numa resposta.
    """

    user: User
    password_hash: str


@dataclass(frozen=True, slots=True)
class UpdateUser(BaseUpdateCommand):
    """Campos do próprio usuário editáveis pela gestão de perfil. `UNSET` = não mexer.

    E-mail, perfil (`role`) e status (`is_active`) não entram aqui: mudam pelo
    cadastro administrado por um admin — que a Sprint 2 ainda não expõe —, não
    pela autoedição do próprio usuário.
    """

    name: str | Unset = UNSET
    phone: str | Unset | None = UNSET
