"""Montagem do router raiz.

Único ponto da aplicação que conhece todos os módulos — é o que permite a
`app/core` não conhecer nenhum.
"""

from fastapi import APIRouter

from app.modules.clients.adapters.http.router import router as clients_router
from app.modules.health.router import router as health_router
from app.modules.service_requests.adapters.http.public_router import (
    public_router as public_service_requests_router,
)
from app.modules.service_requests.adapters.http.router import (
    client_history_router as client_service_requests_router,
)
from app.modules.service_requests.adapters.http.router import (
    router as service_requests_router,
)
from app.modules.users.adapters.http.router import auth_router, users_router


def build_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(health_router, prefix="/health", tags=["Health"])
    router.include_router(auth_router, prefix="/auth", tags=["Autenticação"])
    router.include_router(users_router, prefix="/users", tags=["Usuários"])
    router.include_router(clients_router, prefix="/clients", tags=["Clientes"])
    # Histórico na ficha do cliente (`/clients/{id}/service-requests`): fica
    # depois do router de clientes, mas não há colisão — o `/{client_id}` dele
    # casa um único segmento de caminho.
    router.include_router(
        client_service_requests_router, prefix="/clients", tags=["Solicitações"]
    )
    router.include_router(
        service_requests_router, prefix="/service-requests", tags=["Solicitações"]
    )
    # Entrada pública (sem autenticação) do formulário do site.
    router.include_router(
        public_service_requests_router,
        prefix="/public/service-requests",
        tags=["Site público"],
    )
    return router


api_router = build_api_router()
