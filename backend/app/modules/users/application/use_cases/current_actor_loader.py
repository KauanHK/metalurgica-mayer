import uuid

from app.core.actors import UserActor
from app.core.exceptions import UnauthorizedError
from app.modules.users.application.ports.unit_of_work import UsersUnitOfWorkProtocol


class CurrentActorLoader:
    """Resolve o `UserActor` da requisição a partir do id extraído do token.

    É o que `get_current_subject` (`app/core/security`) não pode fazer sozinho:
    o core sabe decodificar o token, mas quem confere se o usuário ainda existe
    e está ativo é este módulo — `app/core` nunca importa `app/modules`.
    """

    def __init__(self, uow: UsersUnitOfWorkProtocol) -> None:
        self._uow = uow

    async def load(self, user_id: uuid.UUID) -> UserActor:
        async with self._uow as uow:
            user = await uow.users.get_by_id_or_none(user_id)

        if user is None or not user.is_active:
            raise UnauthorizedError(
                "Sessão inválida: usuário não encontrado ou inativo."
            )
        return UserActor(user_id=user.id, role=user.role)
