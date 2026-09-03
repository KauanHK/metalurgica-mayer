import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.background import BACKGROUND_TASKS
from app.api.router import api_router
from app.api.startup_checks import STARTUP_CHECKS
from app.core.db.session import db
from app.core.handlers import register_exception_handlers
from app.core.logging_config import configure_logging
from app.core.middleware import setup_middleware
from app.core.settings import settings

logger = logging.getLogger(__name__)


def mount_routes(app: FastAPI) -> None:
    """Monta o router raiz sob `/api`.

    O prefixo fica aqui, e não nos módulos, porque é decisão de publicação: é
    ele que o nginx usa para separar a API do front na mesma origem.
    """

    app.include_router(api_router, prefix="/api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Ciclo de vida da aplicação: abre o banco, roda diagnósticos e workers."""

    db.init()

    # Diagnóstico de configuração: nada aqui pode impedir a app de subir.
    for check in STARTUP_CHECKS:
        try:
            check()
        except Exception:
            logger.exception("Falha na verificação de startup %s", check.__name__)

    tasks: list[asyncio.Task[None]] = [
        asyncio.create_task(task()) for task in BACKGROUND_TASKS
    ]

    try:
        yield
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await db.close()


def create_app() -> FastAPI:
    """Fábrica da aplicação: handlers, middleware, rotas e lifespan."""

    configure_logging()

    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        summary="ERP e site institucional da Metalúrgica Mayer",
        lifespan=lifespan,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        redoc_url="/api/redoc",
    )

    register_exception_handlers(app)
    setup_middleware(app)
    mount_routes(app)

    return app
