"""Testes da entrada pública de solicitações (`POST /public/service-requests`)."""

from typing import Any

from httpx import AsyncClient

from app.core.dates import today_br
from tests.integration.modules.service_requests.conftest import (
    create_client,
    create_service_request,
)

URL = "/public/service-requests"

# CPF e CNPJ válidos (de teste).
CPF = "52998224725"
CPF_MASCARADO = "529.982.247-25"
CNPJ = "11222333000181"


def payload(**overrides: Any) -> dict[str, Any]:
    """Corpo válido do formulário do site, com os campos sobrescritos."""

    base: dict[str, Any] = {
        "name": "Maria Souza",
        "email": "maria@exemplo.com.br",
        "phone": "47999990000",
        "title": "Portão de garagem",
        "description": "Preciso de um portão deslizante de 4 metros.",
    }
    return {**base, **overrides}


async def list_clients(client: AsyncClient, headers) -> list[dict[str, Any]]:
    response = await client.get("/clients?page_size=100", headers=headers)
    assert response.status_code == 200, response.text
    items: list[dict[str, Any]] = response.json()["data"]
    return items


async def list_requests(
    client: AsyncClient, headers, query: str = ""
) -> list[dict[str, Any]]:
    response = await client.get(
        f"/service-requests?page_size=100{query}", headers=headers
    )
    assert response.status_code == 200, response.text
    items: list[dict[str, Any]] = response.json()["data"]
    return items


class TestEnvio:
    async def test_funciona_sem_token_e_devolve_comprovante_enxuto(
        self, client: AsyncClient
    ) -> None:
        response = await client.post(URL, json=payload())

        assert response.status_code == 201
        body = response.json()
        assert set(body) == {"id", "status"}
        assert body["status"] == "open"
        assert body["id"]

    async def test_solicitacao_nasce_aberta_com_origem_site_e_data_de_hoje(
        self, client: AsyncClient, auth_headers
    ) -> None:
        response = await client.post(URL, json=payload())

        detalhe = await client.get(
            f"/service-requests/{response.json()['id']}", headers=auth_headers
        )
        assert detalhe.status_code == 200
        body = detalhe.json()
        assert body["status"] == "open"
        assert body["origin"] == "website"
        assert body["requested_at"] == today_br().isoformat()
        assert body["due_date"] is None
        assert body["title"] == "Portão de garagem"
        assert body["description"] == "Preciso de um portão deslizante de 4 metros."

    async def test_cliente_novo_e_criado_ativo_e_vinculado(
        self, client: AsyncClient, auth_headers
    ) -> None:
        response = await client.post(
            URL, json=payload(document=CPF_MASCARADO, email="Maria@Exemplo.com.br")
        )

        assert response.status_code == 201
        clientes = await list_clients(client, auth_headers)
        assert len(clientes) == 1
        novo = clientes[0]
        assert novo["name"] == "Maria Souza"
        assert novo["document"] == CPF
        assert novo["phone"] == "47999990000"
        assert novo["email"].lower() == "maria@exemplo.com.br"
        assert novo["is_active"] is True
        assert novo["notes"] == "Cadastrado pelo site"

        solicitacao = (
            await client.get(
                f"/service-requests/{response.json()['id']}", headers=auth_headers
            )
        ).json()
        assert solicitacao["client_id"] == novo["id"]
        assert solicitacao["client_name"] == "Maria Souza"

    async def test_texto_e_aparado_e_campos_opcionais_vazios_viram_nulos(
        self, client: AsyncClient, auth_headers
    ) -> None:
        response = await client.post(
            URL,
            json=payload(
                name="  Maria Souza  ",
                title="  Portão  ",
                description="  Portão simples, com fechadura.  ",
                document="  ",
                email="",
            ),
        )

        assert response.status_code == 201
        cliente = (await list_clients(client, auth_headers))[0]
        assert cliente["name"] == "Maria Souza"
        assert cliente["document"] is None
        assert cliente["email"] is None
        solicitacao = (
            await client.get(
                f"/service-requests/{response.json()['id']}", headers=auth_headers
            )
        ).json()
        assert solicitacao["title"] == "Portão"
        assert solicitacao["description"] == "Portão simples, com fechadura."

    async def test_aceita_so_telefone_sem_email(
        self, client: AsyncClient, auth_headers
    ) -> None:
        response = await client.post(URL, json=payload(email=None))

        assert response.status_code == 201
        assert (await list_clients(client, auth_headers))[0]["email"] is None

    async def test_aceita_so_email_sem_telefone(
        self, client: AsyncClient, auth_headers
    ) -> None:
        response = await client.post(URL, json=payload(phone=""))

        assert response.status_code == 201
        assert (await list_clients(client, auth_headers))[0]["phone"] is None

    async def test_dois_envios_do_mesmo_solicitante_geram_um_cliente(
        self, client: AsyncClient, auth_headers
    ) -> None:
        primeiro = await client.post(URL, json=payload())
        segundo = await client.post(URL, json=payload(title="Grade de janela"))

        assert primeiro.status_code == segundo.status_code == 201
        assert primeiro.json()["id"] != segundo.json()["id"]
        clientes = await list_clients(client, auth_headers)
        assert len(clientes) == 1
        historico = await client.get(
            f"/clients/{clientes[0]['id']}/service-requests", headers=auth_headers
        )
        assert historico.json()["total"] == 2


class TestClienteExistente:
    async def test_reaproveita_cliente_por_email_sem_diferenciar_caixa(
        self, client: AsyncClient, auth_headers
    ) -> None:
        existente = (
            await client.post(
                "/clients",
                json={"name": "Serralheria Silva", "email": "contato@silva.com.br"},
                headers=auth_headers,
            )
        ).json()

        response = await client.post(
            URL, json=payload(name="Outro Nome", email="CONTATO@Silva.com.br")
        )

        assert response.status_code == 201
        assert len(await list_clients(client, auth_headers)) == 1
        solicitacao = (
            await client.get(
                f"/service-requests/{response.json()['id']}", headers=auth_headers
            )
        ).json()
        assert solicitacao["client_id"] == existente["id"]
        assert solicitacao["origin"] == "website"

    async def test_reaproveita_cliente_por_documento(
        self, client: AsyncClient, auth_headers
    ) -> None:
        existente = (
            await client.post(
                "/clients",
                json={"name": "Metalúrgica Alfa", "document": CNPJ},
                headers=auth_headers,
            )
        ).json()

        response = await client.post(
            URL,
            json=payload(document="11.222.333/0001-81", email="outro@alfa.com.br"),
        )

        assert response.status_code == 201
        assert len(await list_clients(client, auth_headers)) == 1
        solicitacao = (
            await client.get(
                f"/service-requests/{response.json()['id']}", headers=auth_headers
            )
        ).json()
        assert solicitacao["client_id"] == existente["id"]

    async def test_nao_altera_os_dados_do_cliente_existente(
        self, client: AsyncClient, auth_headers
    ) -> None:
        existente = (
            await client.post(
                "/clients",
                json={
                    "name": "Serralheria Silva",
                    "document": CPF,
                    "email": "contato@silva.com.br",
                    "phone": "4733330000",
                    "city": "Massaranduba",
                    "notes": "Cliente antigo",
                },
                headers=auth_headers,
            )
        ).json()

        response = await client.post(
            URL,
            json=payload(
                name="Impostor",
                document=CPF,
                email="contato@silva.com.br",
                phone="47911112222",
            ),
        )

        assert response.status_code == 201
        depois = (
            await client.get(f"/clients/{existente['id']}", headers=auth_headers)
        ).json()
        assert depois == existente

    async def test_cliente_inativo_recebe_a_solicitacao_sem_ser_reativado(
        self, client: AsyncClient, auth_headers
    ) -> None:
        inativo = (
            await client.post(
                "/clients",
                json={
                    "name": "Antiga Serralheria",
                    "email": "antiga@serralheria.com.br",
                    "is_active": False,
                },
                headers=auth_headers,
            )
        ).json()

        response = await client.post(
            URL, json=payload(email="antiga@serralheria.com.br")
        )

        assert response.status_code == 201
        depois = (
            await client.get(f"/clients/{inativo['id']}", headers=auth_headers)
        ).json()
        assert depois["is_active"] is False
        assert len(await list_clients(client, auth_headers)) == 1
        historico = await client.get(
            f"/clients/{inativo['id']}/service-requests", headers=auth_headers
        )
        assert historico.json()["total"] == 1

    async def test_email_de_cliente_com_outro_documento_gera_cliente_novo(
        self, client: AsyncClient, auth_headers
    ) -> None:
        existente = (
            await client.post(
                "/clients",
                json={
                    "name": "Metalúrgica Alfa",
                    "document": CNPJ,
                    "email": "compartilhado@exemplo.com.br",
                },
                headers=auth_headers,
            )
        ).json()

        response = await client.post(
            URL, json=payload(document=CPF, email="compartilhado@exemplo.com.br")
        )

        assert response.status_code == 201
        clientes = await list_clients(client, auth_headers)
        assert len(clientes) == 2
        solicitacao = (
            await client.get(
                f"/service-requests/{response.json()['id']}", headers=auth_headers
            )
        ).json()
        assert solicitacao["client_id"] != existente["id"]

    async def test_documento_novo_com_email_de_cliente_sem_documento_vincula_a_ele(
        self, client: AsyncClient, auth_headers
    ) -> None:
        existente = (
            await client.post(
                "/clients",
                json={"name": "Silva", "email": "silva@exemplo.com.br"},
                headers=auth_headers,
            )
        ).json()

        response = await client.post(
            URL, json=payload(document=CPF, email="silva@exemplo.com.br")
        )

        solicitacao = (
            await client.get(
                f"/service-requests/{response.json()['id']}", headers=auth_headers
            )
        ).json()
        assert solicitacao["client_id"] == existente["id"]
        depois = (
            await client.get(f"/clients/{existente['id']}", headers=auth_headers)
        ).json()
        assert depois["document"] is None

    async def test_resposta_nao_revela_se_o_solicitante_ja_era_cliente(
        self, client: AsyncClient, auth_headers
    ) -> None:
        await create_client(client, auth_headers, name="Serralheria Silva")
        await client.post(
            "/clients",
            json={"name": "Conhecido", "email": "conhecido@exemplo.com.br"},
            headers=auth_headers,
        )

        novo = await client.post(URL, json=payload(email="novo@exemplo.com.br"))
        conhecido = await client.post(
            URL, json=payload(email="conhecido@exemplo.com.br")
        )

        assert novo.status_code == conhecido.status_code == 201
        assert set(novo.json()) == set(conhecido.json()) == {"id", "status"}
        for resposta in (novo, conhecido):
            texto = resposta.text
            assert "client" not in texto
            assert "Conhecido" not in texto
            assert "conhecido@exemplo.com.br" not in texto


class TestHoneypot:
    async def test_honeypot_preenchido_responde_201_sem_gravar(
        self, client: AsyncClient, auth_headers
    ) -> None:
        response = await client.post(URL, json=payload(website="http://spam.example"))

        assert response.status_code == 201
        assert set(response.json()) == {"id", "status"}
        assert response.json()["status"] == "open"
        assert await list_clients(client, auth_headers) == []
        assert await list_requests(client, auth_headers) == []

    async def test_honeypot_vazio_ou_em_branco_nao_conta_como_robo(
        self, client: AsyncClient, auth_headers
    ) -> None:
        for valor in ("", "   ", None):
            response = await client.post(
                URL, json=payload(website=valor, email=f"x{len(str(valor))}@a.com")
            )
            assert response.status_code == 201

        assert len(await list_requests(client, auth_headers)) == 3


class TestValidacao:
    async def test_sem_email_e_sem_telefone_devolve_422(
        self, client: AsyncClient, auth_headers
    ) -> None:
        response = await client.post(URL, json=payload(email=None, phone=""))

        assert response.status_code == 422
        assert response.json()["code"] == "validation_error"
        assert "contato" in response.json()["details"][0]["message"]
        assert await list_clients(client, auth_headers) == []

    async def test_campos_obrigatorios_ausentes_devolvem_422(
        self, client: AsyncClient
    ) -> None:
        for campo in ("name", "title", "description"):
            corpo = payload()
            del corpo[campo]

            response = await client.post(URL, json=corpo)

            assert response.status_code == 422, campo
            assert response.json()["details"][0]["field"] == campo

    async def test_email_invalido_devolve_422(self, client: AsyncClient) -> None:
        response = await client.post(URL, json=payload(email="isso-nao-e-email"))

        assert response.status_code == 422
        assert response.json()["details"][0]["field"] == "email"

    async def test_documento_invalido_devolve_422(self, client: AsyncClient) -> None:
        response = await client.post(URL, json=payload(document="11111111111"))

        assert response.status_code == 422
        assert response.json()["details"][0]["field"] == "document"

    async def test_titulo_curto_devolve_422(self, client: AsyncClient) -> None:
        response = await client.post(URL, json=payload(title="ab"))

        assert response.status_code == 422
        assert response.json()["details"][0]["field"] == "title"

    async def test_nome_curto_devolve_422(self, client: AsyncClient) -> None:
        response = await client.post(URL, json=payload(name="M"))

        assert response.status_code == 422
        assert response.json()["details"][0]["field"] == "name"

    async def test_descricao_em_branco_devolve_422(self, client: AsyncClient) -> None:
        response = await client.post(URL, json=payload(description="     "))

        assert response.status_code == 422
        assert response.json()["details"][0]["field"] == "description"

    async def test_descricao_acima_do_limite_devolve_422(
        self, client: AsyncClient, auth_headers
    ) -> None:
        longa = await client.post(URL, json=payload(description="a" * 5001))
        no_limite = await client.post(URL, json=payload(description="a" * 5000))

        assert longa.status_code == 422
        assert longa.json()["details"][0]["field"] == "description"
        assert no_limite.status_code == 201

    async def test_telefone_acima_do_limite_devolve_422(
        self, client: AsyncClient
    ) -> None:
        response = await client.post(URL, json=payload(phone="1" * 21))

        assert response.status_code == 422
        assert response.json()["details"][0]["field"] == "phone"

    async def test_tipos_errados_devolvem_422_e_nao_500(
        self, client: AsyncClient
    ) -> None:
        response = await client.post(
            URL, json=payload(phone=4799999, document=123, email=1)
        )

        assert response.status_code == 422


class TestVisibilidadeNoSistemaInterno:
    async def test_aparece_na_listagem_e_no_historico_do_cliente(
        self, client: AsyncClient, auth_headers
    ) -> None:
        response = await client.post(URL, json=payload(document=CPF))

        listagem = await list_requests(client, auth_headers)
        assert [s["id"] for s in listagem] == [response.json()["id"]]
        cliente_id = listagem[0]["client_id"]
        historico = await client.get(
            f"/clients/{cliente_id}/service-requests", headers=auth_headers
        )
        assert historico.status_code == 200
        assert [s["id"] for s in historico.json()["data"]] == [response.json()["id"]]

    async def test_listagem_continua_exigindo_token(self, client: AsyncClient) -> None:
        await client.post(URL, json=payload())

        assert (await client.get("/service-requests")).status_code == 401
        assert (await client.get("/clients")).status_code == 401


class TestFiltroPorOrigem:
    async def _montar(self, client: AsyncClient, auth_headers) -> dict[str, Any]:
        interno_cliente = await create_client(
            client, auth_headers, name="Cliente Interno"
        )
        interna = await create_service_request(
            client, auth_headers, interno_cliente["id"], title="Pedido interno"
        )
        site = (await client.post(URL, json=payload(title="Pedido do site"))).json()
        # Um pedido do site também no histórico do cliente interno.
        site_mesmo_cliente = (
            await client.post(
                URL,
                json=payload(
                    name="Cliente Interno",
                    email="x@y.com",
                    document=None,
                    title="Segundo do site",
                ),
            )
        ).json()
        return {
            "cliente_interno": interno_cliente,
            "interna": interna,
            "site": site,
            "site_mesmo_cliente": site_mesmo_cliente,
        }

    async def test_filtra_listagem_por_origem(
        self, client: AsyncClient, auth_headers
    ) -> None:
        dados = await self._montar(client, auth_headers)

        do_site = await list_requests(client, auth_headers, "&origin=website")
        internas = await list_requests(client, auth_headers, "&origin=internal")
        todas = await list_requests(client, auth_headers)

        assert {s["id"] for s in do_site} == {
            dados["site"]["id"],
            dados["site_mesmo_cliente"]["id"],
        }
        assert {s["origin"] for s in do_site} == {"website"}
        assert [s["id"] for s in internas] == [dados["interna"]["id"]]
        assert len(todas) == 3

    async def test_filtra_historico_do_cliente_por_origem(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers, name="Serralheria Silva")
        await create_service_request(client, auth_headers, cliente["id"])
        # Cliente criado acima não tem e-mail; ligamos o pedido do site a ele pelo
        # documento, informado numa edição.
        await client.patch(
            f"/clients/{cliente['id']}", json={"document": CPF}, headers=auth_headers
        )
        site = await client.post(URL, json=payload(document=CPF))

        historico_site = await client.get(
            f"/clients/{cliente['id']}/service-requests?origin=website",
            headers=auth_headers,
        )
        historico_interno = await client.get(
            f"/clients/{cliente['id']}/service-requests?origin=internal",
            headers=auth_headers,
        )

        assert [s["id"] for s in historico_site.json()["data"]] == [site.json()["id"]]
        assert historico_interno.json()["total"] == 1
        assert historico_interno.json()["data"][0]["origin"] == "internal"

    async def test_origem_invalida_devolve_422(
        self, client: AsyncClient, auth_headers
    ) -> None:
        response = await client.get(
            "/service-requests?origin=fax", headers=auth_headers
        )

        assert response.status_code == 422
