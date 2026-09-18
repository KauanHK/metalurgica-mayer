"""Testes dos endpoints de gestão de perfil (`/users/me`)."""

from httpx import AsyncClient

from app.modules.users.adapters.db.models import User as UserModel
from tests.integration.modules.users.conftest import PASSWORD


async def _login_headers(client: AsyncClient, email: str) -> dict[str, str]:
    login = await client.post(
        "/auth/login", json={"email": email, "password": PASSWORD}
    )
    token: str = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestGetProfile:
    async def test_sem_token_devolve_401(self, client: AsyncClient) -> None:
        response = await client.get("/users/me")

        assert response.status_code == 401

    async def test_com_token_devolve_o_proprio_usuario(
        self, client: AsyncClient, existing_user
    ) -> None:
        headers = await _login_headers(client, existing_user.email)

        response = await client.get("/users/me", headers=headers)

        assert response.status_code == 200
        assert response.json()["id"] == str(existing_user.id)

    async def test_com_token_de_usuario_desativado_depois_do_login_devolve_401(
        self, client: AsyncClient, existing_user, session_factory
    ) -> None:
        headers = await _login_headers(client, existing_user.email)

        session = session_factory()
        model = await session.get(UserModel, existing_user.id)
        assert model is not None
        model.is_active = False
        await session.commit()

        response = await client.get("/users/me", headers=headers)

        assert response.status_code == 401


class TestUpdateProfile:
    async def test_altera_nome_e_telefone(
        self, client: AsyncClient, existing_user
    ) -> None:
        headers = await _login_headers(client, existing_user.email)

        response = await client.patch(
            "/users/me",
            json={"name": "Novo Nome", "phone": "47999990000"},
            headers=headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "Novo Nome"
        assert body["phone"] == "47999990000"

    async def test_nao_altera_campo_ausente_do_corpo(
        self, client: AsyncClient, existing_user
    ) -> None:
        headers = await _login_headers(client, existing_user.email)

        response = await client.patch(
            "/users/me", json={"name": "Só o Nome"}, headers=headers
        )

        assert response.status_code == 200
        assert response.json()["phone"] == existing_user.phone

    async def test_sem_token_devolve_401(self, client: AsyncClient) -> None:
        response = await client.patch("/users/me", json={"name": "Alguém"})

        assert response.status_code == 401


class TestChangePassword:
    async def test_com_senha_atual_correta_troca_a_senha(
        self, client: AsyncClient, existing_user
    ) -> None:
        headers = await _login_headers(client, existing_user.email)

        response = await client.post(
            "/users/me/password",
            json={"current_password": PASSWORD, "new_password": "nova-senha-123"},
            headers=headers,
        )
        assert response.status_code == 204

        old_login = await client.post(
            "/auth/login", json={"email": existing_user.email, "password": PASSWORD}
        )
        assert old_login.status_code == 401

        new_login = await client.post(
            "/auth/login",
            json={"email": existing_user.email, "password": "nova-senha-123"},
        )
        assert new_login.status_code == 200

    async def test_com_senha_atual_errada_devolve_401_e_nao_troca_a_senha(
        self, client: AsyncClient, existing_user
    ) -> None:
        headers = await _login_headers(client, existing_user.email)

        response = await client.post(
            "/users/me/password",
            json={"current_password": "senha-errada", "new_password": "nova-senha-123"},
            headers=headers,
        )
        assert response.status_code == 401

        still_works = await client.post(
            "/auth/login", json={"email": existing_user.email, "password": PASSWORD}
        )
        assert still_works.status_code == 200

    async def test_com_senha_nova_curta_demais_devolve_422(
        self, client: AsyncClient, existing_user
    ) -> None:
        headers = await _login_headers(client, existing_user.email)

        response = await client.post(
            "/users/me/password",
            json={"current_password": PASSWORD, "new_password": "curta"},
            headers=headers,
        )

        assert response.status_code == 422
