"""Fixtures dos testes de solicitações de serviço."""

from typing import Any

import pytest_asyncio
from httpx import AsyncClient

from tests.integration.conftest import PASSWORD


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, existing_user) -> dict[str, str]:
    """Cabeçalho de autorização de um usuário ativo."""

    login = await client.post(
        "/auth/login", json={"email": existing_user.email, "password": PASSWORD}
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


async def create_client(
    client: AsyncClient,
    headers: dict[str, str],
    *,
    name: str = "Serralheria Silva",
    is_active: bool = True,
) -> dict[str, Any]:
    """Cadastra um cliente pela API e devolve o corpo da resposta."""

    response = await client.post(
        "/clients", json={"name": name, "is_active": is_active}, headers=headers
    )
    assert response.status_code == 201, response.text
    body: dict[str, Any] = response.json()
    return body


async def create_service_request(
    client: AsyncClient,
    headers: dict[str, str],
    client_id: str,
    **fields: Any,
) -> dict[str, Any]:
    """Cadastra uma solicitação pela API e devolve o corpo da resposta."""

    payload = {"client_id": client_id, "title": "Portão de garagem", **fields}
    response = await client.post("/service-requests", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    body: dict[str, Any] = response.json()
    return body
