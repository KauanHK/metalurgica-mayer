import uuid
from dataclasses import dataclass

from app.core.actors.roles import UserRole


@dataclass(frozen=True, slots=True)
class UserActor:
    """Quem está executando a operação.

    É o mínimo que os use cases precisam saber do usuário autenticado: id para
    auditoria e perfil para autorização. Carregar a entidade `User` inteira
    acoplaria todo módulo ao formato do cadastro de usuários.
    """

    user_id: uuid.UUID
    role: UserRole

    @property
    def is_admin(self) -> bool:
        """Indica se o ator tem perfil de administrador."""

        return self.role is UserRole.ADMIN
