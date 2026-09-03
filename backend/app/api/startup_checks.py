"""Verificações executadas uma vez, na subida da aplicação.

Mesmo papel de `app/api/background.py`: conhece o que o core não pode conhecer.

Um check **nunca** impede a app de subir — ele registra no log e retorna. O que
é inaceitável a ponto de derrubar o processo pertence ao validador de
`Settings`, que roda antes.
"""

import logging
from collections.abc import Callable

from app.core.settings import settings

logger = logging.getLogger(__name__)

StartupCheck = Callable[[], None]

# Segredo do template de `.env.example`. Serve em dev; em produção é uma chave
# pública de fato, e qualquer um pode assinar um token de administrador com ela.
_JWT_SECRET_INSEGURO = "troque-este-valor-em-producao"


def log_environment() -> None:
    """Registra em que ambiente e contra qual banco esta instância subiu.

    Serve para abrir o log e responder "esta instância está falando com qual
    banco?" sem adivinhação. A senha é omitida de propósito.
    """

    logger.info(
        "Ambiente: %s | banco: %s@%s:%s/%s | log level: %s",
        settings.ENVIRONMENT,
        settings.POSTGRES_USER,
        settings.POSTGRES_HOST,
        settings.POSTGRES_PORT,
        settings.POSTGRES_DB,
        settings.LOG_LEVEL,
    )


def check_jwt_secret() -> None:
    """Avisa quando a produção subiu com o segredo de exemplo."""

    if settings.ENVIRONMENT == "local":
        return

    if settings.JWT_SECRET == _JWT_SECRET_INSEGURO or len(settings.JWT_SECRET) < 32:
        logger.error(
            "JWT_SECRET fraco ou igual ao do .env.example em ambiente '%s'. "
            "Gere um novo com `openssl rand -hex 32` — com este valor, qualquer "
            "pessoa consegue assinar um token válido.",
            settings.ENVIRONMENT,
        )


STARTUP_CHECKS: list[StartupCheck] = [log_environment, check_jwt_secret]
