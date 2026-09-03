import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TypedDict, cast

from app.core.exceptions import UnauthorizedError
from app.core.security.jwt import create_token, decode_token
from app.core.settings import settings


@dataclass(frozen=True, slots=True)
class TokenIdentity:
    """Quem o token identifica (vai no claim `sub`)."""

    subject: uuid.UUID


class Claims(TypedDict):
    sub: str
    type: str
    iat: datetime
    exp: datetime


def create_access_token(identity: TokenIdentity) -> str:
    """Emite o token de acesso, curto, usado em cada requisição."""

    now = datetime.now(tz=UTC)
    return create_token(
        claims=Claims(
            sub=str(identity.subject),
            type="access",
            iat=now,
            exp=now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_MIN),
        )
    )


def create_refresh_token(identity: TokenIdentity) -> str:
    """Emite o token de renovação, longo, guardado só para renovar o acesso."""

    now = datetime.now(tz=UTC)
    return create_token(
        claims=Claims(
            sub=str(identity.subject),
            type="refresh",
            iat=now,
            exp=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRES_DAYS),
        )
    )


def _decode_typed(token: str, expected: str) -> Claims:
    """Decodifica conferindo o tipo do token.

    O `type` impede que um refresh token — de vida longa — seja aceito como
    credencial de acesso.
    """

    claims = decode_token(token=token)
    if claims.get("type") != expected:
        raise UnauthorizedError("Token inválido para esta operação.")
    # O payload já passou pela verificação de assinatura e de expiração do PyJWT;
    # o cast só devolve ao dicionário o formato que nós mesmos assinamos.
    return cast(Claims, claims)


def decode_access_token(token: str) -> Claims:
    """Decodifica e valida um token de acesso."""

    return _decode_typed(token, "access")


def decode_refresh_token(token: str) -> Claims:
    """Decodifica e valida um token de renovação."""

    return _decode_typed(token, "refresh")
