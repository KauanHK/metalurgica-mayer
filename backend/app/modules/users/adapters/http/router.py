"""Rotas de autenticação (`/auth`) e de gestão do próprio perfil (`/users/me`).

`auth_router` é público: é por ele que alguém obtém um token, então nenhuma
rota aqui pode depender de `get_current_actor`. `users_router` é o oposto —
toda rota exige `CurrentActorDep`, e sempre atua sobre o dono do token, nunca
sobre um id arbitrário: a Sprint 2 ainda não tem edição de outro usuário por um
admin.
"""

import uuid

from fastapi import APIRouter, status

from app.core.exceptions import UnauthorizedError
from app.core.security.access_tokens import (
    TokenIdentity,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.modules.users.adapters.http.dependencies import (
    CurrentActorDep,
    UsersUnitOfWorkDep,
)
from app.modules.users.adapters.http.schemas import (
    AccessTokenResponse,
    LoginRequest,
    LoginResponse,
    PasswordChange,
    ProfileUpdate,
    RefreshRequest,
    UserRead,
)
from app.modules.users.application.dtos.commands import (
    ChangePasswordCommand,
    UpdateProfileCommand,
)
from app.modules.users.application.use_cases.authenticator import Authenticator
from app.modules.users.application.use_cases.current_actor_loader import (
    CurrentActorLoader,
)
from app.modules.users.application.use_cases.password_changer import PasswordChanger
from app.modules.users.application.use_cases.users_reader import UsersReader
from app.modules.users.application.use_cases.users_updater import UsersUpdater

auth_router = APIRouter()
users_router = APIRouter()


@auth_router.post("/login", response_model=LoginResponse, summary="Autenticar")
async def login(data: LoginRequest, uow: UsersUnitOfWorkDep) -> LoginResponse:
    """Confere e-mail e senha e devolve o par de tokens mais o usuário."""

    user = await Authenticator(uow=uow).authenticate(
        email=data.email, password=data.password
    )
    identity = TokenIdentity(subject=user.id)
    return LoginResponse(
        access_token=create_access_token(identity),
        refresh_token=create_refresh_token(identity),
        user=UserRead.model_validate(user.to_dict()),
    )


@auth_router.post(
    "/refresh", response_model=AccessTokenResponse, summary="Renovar token de acesso"
)
async def refresh(data: RefreshRequest, uow: UsersUnitOfWorkDep) -> AccessTokenResponse:
    """Troca um refresh token válido por um novo access token.

    Não emite um refresh token novo: sem uma lista de revogação, "rotacionar" o
    refresh token não invalidaria o antigo, então não traria segurança
    nenhuma — só complicaria o front por nada.
    """

    claims = decode_refresh_token(data.refresh_token)
    try:
        subject = uuid.UUID(claims["sub"])
    except (KeyError, ValueError) as exc:
        raise UnauthorizedError("Token inválido.") from exc

    actor = await CurrentActorLoader(uow=uow).load(subject)
    return AccessTokenResponse(
        access_token=create_access_token(TokenIdentity(subject=actor.user_id))
    )


@users_router.get("/me", response_model=UserRead, summary="Consultar o próprio perfil")
async def get_profile(actor: CurrentActorDep, uow: UsersUnitOfWorkDep) -> UserRead:
    """Devolve os dados do usuário autenticado."""

    user = await UsersReader(uow=uow).get_by_id(actor.user_id)
    return UserRead.model_validate(user.to_dict())


@users_router.patch("/me", response_model=UserRead, summary="Editar o próprio perfil")
async def update_profile(
    data: ProfileUpdate, actor: CurrentActorDep, uow: UsersUnitOfWorkDep
) -> UserRead:
    """Altera nome e/ou telefone do usuário autenticado."""

    user = await UsersUpdater(uow=uow).update(
        actor.user_id,
        # `exclude_unset` preserva a semântica do PATCH: campo ausente vira
        # `UNSET` no comando, e o repositório não o toca.
        UpdateProfileCommand(**data.model_dump(exclude_unset=True)),
    )
    return UserRead.model_validate(user.to_dict())


@users_router.post(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Trocar a própria senha",
)
async def change_password(
    data: PasswordChange, actor: CurrentActorDep, uow: UsersUnitOfWorkDep
) -> None:
    """Troca a senha do usuário autenticado, exigindo a senha atual."""

    await PasswordChanger(uow=uow).change(
        actor.user_id,
        ChangePasswordCommand(
            current_password=data.current_password, new_password=data.new_password
        ),
    )
