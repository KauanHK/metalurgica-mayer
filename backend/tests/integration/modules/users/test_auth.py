"""Testes de login e do fluxo de token (`/auth`)."""

from httpx import AsyncClient

from tests.integration.modules.users.conftest import PASSWORD


class TestLogin:
    async def test_login_com_credenciais_validas_devolve_tokens_e_usuario(
        self, client: AsyncClient, existing_user
    ) -> None:
        response = await client.post(
            "/auth/login",
            json={"email": existing_user.email, "password": PASSWORD},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["access_token"]
        assert body["refresh_token"]
        assert body["token_type"] == "bearer"
        assert body["user"]["email"] == existing_user.email
        assert "password" not in body["user"]
        assert "password_hash" not in body["user"]

    async def test_login_normaliza_email_para_minusculas(
        self, client: AsyncClient, existing_user
    ) -> None:
        response = await client.post(
            "/auth/login",
            json={"email": existing_user.email.upper(), "password": PASSWORD},
        )

        assert response.status_code == 200

    async def test_login_com_senha_errada_devolve_401(
        self, client: AsyncClient, existing_user
    ) -> None:
        response = await client.post(
            "/auth/login",
            json={"email": existing_user.email, "password": "senha-errada"},
        )

        assert response.status_code == 401

    async def test_login_com_email_inexistente_devolve_401(
        self, client: AsyncClient
    ) -> None:
        response = await client.post(
            "/auth/login",
            json={"email": "ninguem@metalurgicamayer.com.br", "password": "qualquer"},
        )

        assert response.status_code == 401

    async def test_login_com_usuario_inativo_devolve_401(
        self, client: AsyncClient, inactive_user
    ) -> None:
        response = await client.post(
            "/auth/login",
            json={"email": inactive_user.email, "password": PASSWORD},
        )

        assert response.status_code == 401


class TestRefresh:
    async def test_refresh_com_token_valido_devolve_novo_access_token(
        self, client: AsyncClient, existing_user
    ) -> None:
        login = await client.post(
            "/auth/login", json={"email": existing_user.email, "password": PASSWORD}
        )
        refresh_token = login.json()["refresh_token"]

        response = await client.post(
            "/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        assert response.json()["access_token"]

    async def test_refresh_com_access_token_no_lugar_do_refresh_devolve_401(
        self, client: AsyncClient, existing_user
    ) -> None:
        login = await client.post(
            "/auth/login", json={"email": existing_user.email, "password": PASSWORD}
        )
        access_token = login.json()["access_token"]

        response = await client.post(
            "/auth/refresh", json={"refresh_token": access_token}
        )

        assert response.status_code == 401

    async def test_refresh_com_token_invalido_devolve_401(
        self, client: AsyncClient
    ) -> None:
        response = await client.post(
            "/auth/refresh", json={"refresh_token": "isto-nao-e-um-jwt"}
        )

        assert response.status_code == 401
