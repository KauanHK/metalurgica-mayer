"""Health check da API.

Raso de propósito: não tem domínio, então não replica o formato hexagonal dos
demais módulos — seria estrutura sem nada dentro. O mesmo vale para
`app/modules/lookups` quando ele existir.
"""

import logging
from typing import Literal

import sqlalchemy as sa
from fastapi import APIRouter, Response
from pydantic import BaseModel

from app.core.db.session import db

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthRead(BaseModel):
    """Situação da API e das suas dependências."""

    status: Literal["ok", "degraded"]
    database: Literal["ok", "unreachable"]


@router.get("", response_model=HealthRead)
async def health(response: Response) -> HealthRead:
    """Informa se a API responde e se o banco está alcançável.

    Responde **503 com corpo** quando o banco não responde, em vez de 200 com um
    campo dizendo que algo vai mal: o healthcheck do Compose e o do orquestrador
    olham o status, não o corpo, e um 200 os faria considerar saudável um
    container que não serve requisição nenhuma.
    """

    try:
        async with db.create_session() as session:
            await session.execute(sa.text("SELECT 1"))
    except Exception:
        logger.exception("Health check: banco de dados inacessível.")
        response.status_code = 503
        return HealthRead(status="degraded", database="unreachable")

    return HealthRead(status="ok", database="ok")
