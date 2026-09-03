import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.core.actors.roles import UserRole

__all__ = ["User", "UserRole"]


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
