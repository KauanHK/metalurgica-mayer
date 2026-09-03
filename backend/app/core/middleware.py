from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings


def setup_middleware(app: FastAPI) -> None:
    """Configura os middlewares da aplicação.

    O CORS é lido de `CORS_ORIGINS` em vez de liberar tudo: em produção o nginx
    serve front e API na mesma origem, então a lista existe para o dev (Next em
    :3000, API em :8000) e não precisa ser um curinga.
    """

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
