"""Montagem do router raiz.

Único ponto da aplicação que conhece todos os módulos — é o que permite a
`app/core` não conhecer nenhum.
"""

from fastapi import APIRouter

from app.modules.clients.adapters.http.router import router as clients_router
from app.modules.health.router import router as health_router
from app.modules.users.adapters.http.router import auth_router, users_router


def build_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(health_router, prefix="/health", tags=["Health"])
    router.include_router(auth_router, prefix="/auth", tags=["Autenticação"])
    router.include_router(users_router, prefix="/users", tags=["Usuários"])
    router.include_router(clients_router, prefix="/clients", tags=["Clientes"])
    return router


api_router = build_api_router()
