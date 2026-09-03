from collections.abc import Mapping
from typing import Any

import jwt as pyjwt

from app.core.exceptions import UnauthorizedError
from app.core.settings import settings


def create_token(claims: Mapping[str, Any]) -> str:
    """Assina um JWT com os claims informados."""

    return pyjwt.encode(
        payload=dict(claims),
        key=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict[str, Any]:
    """Valida e decodifica um JWT, traduzindo qualquer falha em 401."""

    try:
        return pyjwt.decode(
            jwt=token,
            key=settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except pyjwt.ExpiredSignatureError:
        raise UnauthorizedError("Sessão expirada. Faça login novamente.") from None
    except pyjwt.PyJWTError as exc:
        raise UnauthorizedError("Token inválido.") from exc
