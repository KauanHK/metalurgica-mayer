"""Montagem do router raiz.

Único ponto da aplicação que conhece todos os módulos — é o que permite a
`app/core` não conhecer nenhum.
"""

from fastapi import APIRouter

from app.modules.clients.adapters.http.router import router as clients_router
from app.modules.health.router import router as health_router


def build_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(health_router, prefix="/health", tags=["Health"])
    router.include_router(clients_router, prefix="/clients", tags=["Clientes"])
    return router


api_router = build_api_router()
