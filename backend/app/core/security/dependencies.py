import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import UnauthorizedError
from app.core.security.access_tokens import decode_access_token


async def get_current_subject(
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
) -> uuid.UUID:
    """Extrai o `sub` (id do usuário) do token de acesso.

    Resolve apenas o identificador: quem confere se o usuário existe e está
    ativo é `get_current_actor`, no módulo `users` — o core não pode importar
    módulos de domínio.
    """

    claims = decode_access_token(authorization.credentials)
    try:
        return uuid.UUID(claims["sub"])
    except (KeyError, ValueError) as exc:
        raise UnauthorizedError("Token inválido.") from exc


SubjectDep = Annotated[uuid.UUID, Depends(get_current_subject)]
