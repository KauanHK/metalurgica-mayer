from typing import Annotated

from fastapi import Depends

from app.core.actors import UserActor
from app.core.security.dependencies import SubjectDep
from app.modules.users.adapters.db.factories import make_unit_of_work
from app.modules.users.adapters.db.unit_of_work import UsersUnitOfWork
from app.modules.users.application.use_cases.current_actor_loader import (
    CurrentActorLoader,
)

UsersUnitOfWorkDep = Annotated[UsersUnitOfWork, Depends(make_unit_of_work)]


async def get_current_actor(subject: SubjectDep, uow: UsersUnitOfWorkDep) -> UserActor:
    """A dependência que protege uma rota: exige token válido e usuário ativo.

    Outros módulos a importam daqui para proteger seus próprios routers (ver
    `clients/adapters/http/router.py`) — é o único ponto de acoplamento
    intencional entre módulos, porque autenticação é transversal.
    """

    return await CurrentActorLoader(uow=uow).load(subject)


CurrentActorDep = Annotated[UserActor, Depends(get_current_actor)]
