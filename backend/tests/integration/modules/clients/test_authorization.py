"""Confirma que o cadastro de clientes passou a exigir autenticação (Sprint 2)."""

from httpx import AsyncClient

from tests.integration.modules.users.conftest import PASSWORD


class TestClientsRequireAuthentication:
    async def test_listar_sem_token_devolve_401(self, client: AsyncClient) -> None:
        response = await client.get("/clients")

        assert response.status_code == 401

    async def test_listar_com_token_invalido_devolve_401(
        self, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/clients", headers={"Authorization": "Bearer isto-nao-e-um-jwt"}
        )

        assert response.status_code == 401

    async def test_listar_com_token_valido_devolve_200(
        self, client: AsyncClient, existing_user
    ) -> None:
        login = await client.post(
            "/auth/login", json={"email": existing_user.email, "password": PASSWORD}
        )
        token = login.json()["access_token"]

        response = await client.get(
            "/clients", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
