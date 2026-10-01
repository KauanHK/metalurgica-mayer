"""Testes das rotas de solicitações de serviço (`/service-requests`)."""

import uuid
from datetime import date, timedelta

from httpx import AsyncClient

from app.core.dates import today_br
from tests.integration.modules.service_requests.conftest import (
    create_client,
    create_service_request,
)


class TestAuthentication:
    async def test_listar_sem_token_devolve_401(self, client: AsyncClient) -> None:
        response = await client.get("/service-requests")

        assert response.status_code == 401

    async def test_criar_sem_token_devolve_401(self, client: AsyncClient) -> None:
        response = await client.post(
            "/service-requests",
            json={"client_id": str(uuid.uuid4()), "title": "Portão"},
        )

        assert response.status_code == 401

    async def test_consultar_sem_token_devolve_401(self, client: AsyncClient) -> None:
        response = await client.get(f"/service-requests/{uuid.uuid4()}")

        assert response.status_code == 401

    async def test_editar_sem_token_devolve_401(self, client: AsyncClient) -> None:
        response = await client.patch(
            f"/service-requests/{uuid.uuid4()}", json={"title": "Novo título"}
        )

        assert response.status_code == 401

    async def test_historico_do_cliente_sem_token_devolve_401(
        self, client: AsyncClient
    ) -> None:
        response = await client.get(f"/clients/{uuid.uuid4()}/service-requests")

        assert response.status_code == 401


class TestCreate:
    async def test_cria_solicitacao_aberta_com_defaults(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)

        response = await client.post(
            "/service-requests",
            json={
                "client_id": cliente["id"],
                "title": "  Portão de garagem  ",
                "description": "Portão deslizante de 4 m",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        body = response.json()
        assert body["client_id"] == cliente["id"]
        assert body["client_name"] == "Serralheria Silva"
        assert body["title"] == "Portão de garagem"
        assert body["description"] == "Portão deslizante de 4 m"
        assert body["status"] == "open"
        assert body["origin"] == "internal"
        assert body["requested_at"] == today_br().isoformat()
        assert body["due_date"] is None
        assert body["id"]
        assert body["created_at"]

    async def test_aceita_data_e_prazo_informados(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)

        response = await client.post(
            "/service-requests",
            json={
                "client_id": cliente["id"],
                "title": "Estrutura metálica",
                "requested_at": "2026-03-10",
                "due_date": "2026-03-10",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["requested_at"] == "2026-03-10"
        assert response.json()["due_date"] == "2026-03-10"

    async def test_descricao_vazia_vira_nula(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)

        solicitacao = await create_service_request(
            client, auth_headers, cliente["id"], description="   "
        )

        assert solicitacao["description"] is None

    async def test_cliente_inexistente_devolve_422(
        self, client: AsyncClient, auth_headers
    ) -> None:
        response = await client.post(
            "/service-requests",
            json={"client_id": str(uuid.uuid4()), "title": "Portão"},
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert response.json()["code"] == "validation_error"
        assert response.json()["details"][0]["field"] == "client_id"

    async def test_cliente_inativo_devolve_422(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers, is_active=False)

        response = await client.post(
            "/service-requests",
            json={"client_id": cliente["id"], "title": "Portão"},
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert "inativo" in response.json()["message"]

    async def test_prazo_anterior_a_data_da_solicitacao_devolve_422(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)

        response = await client.post(
            "/service-requests",
            json={
                "client_id": cliente["id"],
                "title": "Portão",
                "requested_at": "2026-03-10",
                "due_date": "2026-03-09",
            },
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert response.json()["details"][0]["field"] == "due_date"

    async def test_prazo_no_passado_sem_data_informada_devolve_422(
        self, client: AsyncClient, auth_headers
    ) -> None:
        # Sem `requested_at`, vale hoje: um prazo de ontem fica antes dele.
        cliente = await create_client(client, auth_headers)

        response = await client.post(
            "/service-requests",
            json={
                "client_id": cliente["id"],
                "title": "Portão",
                "due_date": (today_br() - timedelta(days=1)).isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_titulo_curto_devolve_422(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)

        response = await client.post(
            "/service-requests",
            json={"client_id": cliente["id"], "title": "ab"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_sem_cliente_devolve_422(
        self, client: AsyncClient, auth_headers
    ) -> None:
        response = await client.post(
            "/service-requests", json={"title": "Portão"}, headers=auth_headers
        )

        assert response.status_code == 422


class TestGet:
    async def test_consulta_pelo_id(self, client: AsyncClient, auth_headers) -> None:
        cliente = await create_client(client, auth_headers)
        criada = await create_service_request(client, auth_headers, cliente["id"])

        response = await client.get(
            f"/service-requests/{criada['id']}", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json() == criada

    async def test_inexistente_devolve_404(
        self, client: AsyncClient, auth_headers
    ) -> None:
        response = await client.get(
            f"/service-requests/{uuid.uuid4()}", headers=auth_headers
        )

        assert response.status_code == 404


class TestList:
    async def test_lista_vazia(self, client: AsyncClient, auth_headers) -> None:
        response = await client.get("/service-requests", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["data"] == []
        assert response.json()["total"] == 0

    async def test_ordena_da_mais_recente_para_a_mais_antiga(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        for dia, titulo in [(5, "Cinco"), (20, "Vinte"), (12, "Doze")]:
            await create_service_request(
                client,
                auth_headers,
                cliente["id"],
                title=titulo,
                requested_at=date(2026, 3, dia).isoformat(),
            )

        response = await client.get("/service-requests", headers=auth_headers)

        titulos = [item["title"] for item in response.json()["data"]]
        assert titulos == ["Vinte", "Doze", "Cinco"]

    async def test_filtra_por_cliente(self, client: AsyncClient, auth_headers) -> None:
        ana = await create_client(client, auth_headers, name="Ana Metais")
        beto = await create_client(client, auth_headers, name="Beto Ferragens")
        await create_service_request(client, auth_headers, ana["id"], title="Da Ana")
        await create_service_request(client, auth_headers, beto["id"], title="Do Beto")

        response = await client.get(
            "/service-requests", params={"client_id": ana["id"]}, headers=auth_headers
        )

        data = response.json()["data"]
        assert [item["title"] for item in data] == ["Da Ana"]
        assert data[0]["client_name"] == "Ana Metais"
        assert response.json()["total"] == 1

    async def test_filtra_por_status(self, client: AsyncClient, auth_headers) -> None:
        cliente = await create_client(client, auth_headers)
        aberta = await create_service_request(
            client, auth_headers, cliente["id"], title="Aberta"
        )
        em_analise = await create_service_request(
            client, auth_headers, cliente["id"], title="Em análise"
        )
        await client.patch(
            f"/service-requests/{em_analise['id']}",
            json={"status": "in_analysis"},
            headers=auth_headers,
        )

        response = await client.get(
            "/service-requests", params={"status": "open"}, headers=auth_headers
        )

        assert [item["id"] for item in response.json()["data"]] == [aberta["id"]]

    async def test_status_invalido_devolve_422(
        self, client: AsyncClient, auth_headers
    ) -> None:
        response = await client.get(
            "/service-requests", params={"status": "inexistente"}, headers=auth_headers
        )

        assert response.status_code == 422

    async def test_filtra_por_periodo_inclusivo(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        for dia in (1, 10, 15, 20, 28):
            await create_service_request(
                client,
                auth_headers,
                cliente["id"],
                title=f"Dia {dia}",
                requested_at=date(2026, 3, dia).isoformat(),
            )

        response = await client.get(
            "/service-requests",
            params={"date_from": "2026-03-10", "date_to": "2026-03-20"},
            headers=auth_headers,
        )

        titulos = [item["title"] for item in response.json()["data"]]
        assert titulos == ["Dia 20", "Dia 15", "Dia 10"]

    async def test_filtra_so_com_data_inicial(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        for dia in (1, 10, 20):
            await create_service_request(
                client,
                auth_headers,
                cliente["id"],
                title=f"Dia {dia}",
                requested_at=date(2026, 3, dia).isoformat(),
            )

        response = await client.get(
            "/service-requests",
            params={"date_from": "2026-03-10"},
            headers=auth_headers,
        )

        assert response.json()["total"] == 2

    async def test_periodo_invertido_devolve_422(
        self, client: AsyncClient, auth_headers
    ) -> None:
        response = await client.get(
            "/service-requests",
            params={"date_from": "2026-03-20", "date_to": "2026-03-10"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_periodo_invertido_no_historico_devolve_422(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)

        response = await client.get(
            f"/clients/{cliente['id']}/service-requests",
            params={"date_from": "2026-03-20", "date_to": "2026-03-10"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_busca_por_titulo(self, client: AsyncClient, auth_headers) -> None:
        cliente = await create_client(client, auth_headers)
        await create_service_request(
            client, auth_headers, cliente["id"], title="Portão basculante"
        )
        await create_service_request(
            client, auth_headers, cliente["id"], title="Grade de janela"
        )

        response = await client.get(
            "/service-requests", params={"search": "portão"}, headers=auth_headers
        )

        titulos = [item["title"] for item in response.json()["data"]]
        assert titulos == ["Portão basculante"]

    async def test_combina_filtros(self, client: AsyncClient, auth_headers) -> None:
        ana = await create_client(client, auth_headers, name="Ana Metais")
        beto = await create_client(client, auth_headers, name="Beto Ferragens")
        alvo = await create_service_request(
            client, auth_headers, ana["id"], requested_at="2026-03-10"
        )
        await create_service_request(
            client, auth_headers, ana["id"], requested_at="2026-04-10"
        )
        await create_service_request(
            client, auth_headers, beto["id"], requested_at="2026-03-10"
        )

        response = await client.get(
            "/service-requests",
            params={
                "client_id": ana["id"],
                "status": "open",
                "date_from": "2026-03-01",
                "date_to": "2026-03-31",
            },
            headers=auth_headers,
        )

        assert [item["id"] for item in response.json()["data"]] == [alvo["id"]]

    async def test_paginacao(self, client: AsyncClient, auth_headers) -> None:
        cliente = await create_client(client, auth_headers)
        for dia in range(1, 6):
            await create_service_request(
                client,
                auth_headers,
                cliente["id"],
                title=f"Dia {dia}",
                requested_at=date(2026, 3, dia).isoformat(),
            )

        pagina_1 = await client.get(
            "/service-requests",
            params={"page": 1, "page_size": 2},
            headers=auth_headers,
        )
        pagina_3 = await client.get(
            "/service-requests",
            params={"page": 3, "page_size": 2},
            headers=auth_headers,
        )

        assert pagina_1.json()["total"] == 5
        assert pagina_1.json()["total_pages"] == 3
        assert [i["title"] for i in pagina_1.json()["data"]] == ["Dia 5", "Dia 4"]
        assert [i["title"] for i in pagina_3.json()["data"]] == ["Dia 1"]

    async def test_paginacao_estavel_com_mesma_data(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        for n in range(5):
            await create_service_request(
                client,
                auth_headers,
                cliente["id"],
                title=f"Pedido {n}",
                requested_at="2026-03-10",
            )

        ids: list[str] = []
        for page in (1, 2, 3):
            response = await client.get(
                "/service-requests",
                params={"page": page, "page_size": 2},
                headers=auth_headers,
            )
            ids += [item["id"] for item in response.json()["data"]]

        assert len(ids) == 5
        assert len(set(ids)) == 5


class TestUpdate:
    async def test_edita_so_os_campos_enviados(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        criada = await create_service_request(
            client,
            auth_headers,
            cliente["id"],
            description="Original",
            due_date=(today_br() + timedelta(days=10)).isoformat(),
        )

        response = await client.patch(
            f"/service-requests/{criada['id']}",
            json={"title": "Portão social"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["title"] == "Portão social"
        assert body["description"] == "Original"
        assert body["due_date"] == criada["due_date"]
        assert body["status"] == "open"

    async def test_null_limpa_descricao_e_prazo(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        criada = await create_service_request(
            client,
            auth_headers,
            cliente["id"],
            description="Original",
            due_date=(today_br() + timedelta(days=10)).isoformat(),
        )

        response = await client.patch(
            f"/service-requests/{criada['id']}",
            json={"description": None, "due_date": None},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["description"] is None
        assert response.json()["due_date"] is None

    async def test_campos_obrigatorios_nao_aceitam_null(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        criada = await create_service_request(client, auth_headers, cliente["id"])

        for campo in ("title", "status", "requested_at"):
            response = await client.patch(
                f"/service-requests/{criada['id']}",
                json={campo: None},
                headers=auth_headers,
            )
            assert response.status_code == 422, campo

    async def test_corpo_vazio_nao_altera_nada(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        criada = await create_service_request(client, auth_headers, cliente["id"])

        response = await client.patch(
            f"/service-requests/{criada['id']}", json={}, headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["title"] == criada["title"]

    async def test_nao_troca_o_cliente(self, client: AsyncClient, auth_headers) -> None:
        ana = await create_client(client, auth_headers, name="Ana Metais")
        beto = await create_client(client, auth_headers, name="Beto Ferragens")
        criada = await create_service_request(client, auth_headers, ana["id"])

        response = await client.patch(
            f"/service-requests/{criada['id']}",
            json={"client_id": beto["id"]},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["client_id"] == ana["id"]

    async def test_prazo_anterior_a_data_devolve_422(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        criada = await create_service_request(
            client, auth_headers, cliente["id"], requested_at="2026-03-10"
        )

        response = await client.patch(
            f"/service-requests/{criada['id']}",
            json={"due_date": "2026-03-01"},
            headers=auth_headers,
        )

        assert response.status_code == 422
        assert response.json()["details"][0]["field"] == "due_date"

    async def test_mudar_a_data_para_depois_do_prazo_gravado_devolve_422(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        criada = await create_service_request(
            client,
            auth_headers,
            cliente["id"],
            requested_at="2026-03-10",
            due_date="2026-03-15",
        )

        response = await client.patch(
            f"/service-requests/{criada['id']}",
            json={"requested_at": "2026-03-20"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_mudar_data_e_prazo_juntos(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        criada = await create_service_request(
            client,
            auth_headers,
            cliente["id"],
            requested_at="2026-03-10",
            due_date="2026-03-15",
        )

        response = await client.patch(
            f"/service-requests/{criada['id']}",
            json={"requested_at": "2026-03-20", "due_date": "2026-03-25"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["requested_at"] == "2026-03-20"
        assert response.json()["due_date"] == "2026-03-25"

    async def test_inexistente_devolve_404(
        self, client: AsyncClient, auth_headers
    ) -> None:
        response = await client.patch(
            f"/service-requests/{uuid.uuid4()}",
            json={"title": "Novo título"},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestStatusTransitions:
    async def _patch_status(
        self, client: AsyncClient, headers, service_request_id: str, status: str
    ):
        return await client.patch(
            f"/service-requests/{service_request_id}",
            json={"status": status},
            headers=headers,
        )

    async def test_percorre_o_fluxo_normal(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        criada = await create_service_request(client, auth_headers, cliente["id"])

        for novo in ("in_analysis", "in_progress", "completed"):
            response = await self._patch_status(
                client, auth_headers, criada["id"], novo
            )
            assert response.status_code == 200
            assert response.json()["status"] == novo

    async def test_estados_em_andamento_podem_voltar(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        criada = await create_service_request(client, auth_headers, cliente["id"])
        await self._patch_status(client, auth_headers, criada["id"], "in_progress")

        response = await self._patch_status(client, auth_headers, criada["id"], "open")

        assert response.status_code == 200
        assert response.json()["status"] == "open"

    async def test_pode_cancelar_em_qualquer_estado_em_andamento(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        criada = await create_service_request(client, auth_headers, cliente["id"])
        await self._patch_status(client, auth_headers, criada["id"], "in_progress")

        response = await self._patch_status(
            client, auth_headers, criada["id"], "cancelled"
        )

        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"

    async def test_concluida_nao_reabre(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        criada = await create_service_request(client, auth_headers, cliente["id"])
        await self._patch_status(client, auth_headers, criada["id"], "completed")

        for novo in ("open", "in_analysis", "in_progress", "cancelled"):
            response = await self._patch_status(
                client, auth_headers, criada["id"], novo
            )
            assert response.status_code == 409, novo
            assert response.json()["code"] == "conflict"

        atual = await client.get(
            f"/service-requests/{criada['id']}", headers=auth_headers
        )
        assert atual.json()["status"] == "completed"

    async def test_cancelada_nao_reabre(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        criada = await create_service_request(client, auth_headers, cliente["id"])
        await self._patch_status(client, auth_headers, criada["id"], "cancelled")

        for novo in ("open", "in_progress", "completed"):
            response = await self._patch_status(
                client, auth_headers, criada["id"], novo
            )
            assert response.status_code == 409, novo

    async def test_repetir_o_status_terminal_nao_e_conflito(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        criada = await create_service_request(client, auth_headers, cliente["id"])
        await self._patch_status(client, auth_headers, criada["id"], "completed")

        response = await client.patch(
            f"/service-requests/{criada['id']}",
            json={"status": "completed", "description": "Entregue ao cliente"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["description"] == "Entregue ao cliente"

    async def test_status_invalido_devolve_422(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        criada = await create_service_request(client, auth_headers, cliente["id"])

        response = await self._patch_status(
            client, auth_headers, criada["id"], "arquivada"
        )

        assert response.status_code == 422

    async def test_nao_ha_delete(self, client: AsyncClient, auth_headers) -> None:
        cliente = await create_client(client, auth_headers)
        criada = await create_service_request(client, auth_headers, cliente["id"])

        response = await client.delete(
            f"/service-requests/{criada['id']}", headers=auth_headers
        )

        assert response.status_code == 405


class TestClientHistory:
    async def test_lista_so_as_solicitacoes_do_cliente(
        self, client: AsyncClient, auth_headers
    ) -> None:
        ana = await create_client(client, auth_headers, name="Ana Metais")
        beto = await create_client(client, auth_headers, name="Beto Ferragens")
        await create_service_request(
            client,
            auth_headers,
            ana["id"],
            title="Pedido A1",
            requested_at="2026-03-01",
        )
        await create_service_request(
            client,
            auth_headers,
            ana["id"],
            title="Pedido A2",
            requested_at="2026-03-05",
        )
        await create_service_request(
            client, auth_headers, beto["id"], title="Pedido B1"
        )

        response = await client.get(
            f"/clients/{ana['id']}/service-requests", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["total"] == 2
        assert [item["title"] for item in response.json()["data"]] == [
            "Pedido A2",
            "Pedido A1",
        ]

    async def test_filtra_por_status_e_periodo(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        await create_service_request(
            client,
            auth_headers,
            cliente["id"],
            title="Março",
            requested_at="2026-03-10",
        )
        abril = await create_service_request(
            client,
            auth_headers,
            cliente["id"],
            title="Abril",
            requested_at="2026-04-10",
        )
        await client.patch(
            f"/service-requests/{abril['id']}",
            json={"status": "completed"},
            headers=auth_headers,
        )

        por_status = await client.get(
            f"/clients/{cliente['id']}/service-requests",
            params={"status": "completed"},
            headers=auth_headers,
        )
        por_periodo = await client.get(
            f"/clients/{cliente['id']}/service-requests",
            params={"date_from": "2026-03-01", "date_to": "2026-03-31"},
            headers=auth_headers,
        )

        assert [i["title"] for i in por_status.json()["data"]] == ["Abril"]
        assert [i["title"] for i in por_periodo.json()["data"]] == ["Março"]

    async def test_paginacao(self, client: AsyncClient, auth_headers) -> None:
        cliente = await create_client(client, auth_headers)
        for dia in range(1, 4):
            await create_service_request(
                client,
                auth_headers,
                cliente["id"],
                title=f"Dia {dia}",
                requested_at=date(2026, 3, dia).isoformat(),
            )

        response = await client.get(
            f"/clients/{cliente['id']}/service-requests",
            params={"page": 2, "page_size": 2},
            headers=auth_headers,
        )

        assert response.json()["total"] == 3
        assert response.json()["total_pages"] == 2
        assert [i["title"] for i in response.json()["data"]] == ["Dia 1"]

    async def test_cliente_sem_solicitacoes_devolve_lista_vazia(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)

        response = await client.get(
            f"/clients/{cliente['id']}/service-requests", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["data"] == []

    async def test_cliente_inexistente_devolve_404(
        self, client: AsyncClient, auth_headers
    ) -> None:
        response = await client.get(
            f"/clients/{uuid.uuid4()}/service-requests", headers=auth_headers
        )

        assert response.status_code == 404

    async def test_historico_de_cliente_inativo_continua_disponivel(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        await create_service_request(client, auth_headers, cliente["id"])
        await client.patch(
            f"/clients/{cliente['id']}", json={"is_active": False}, headers=auth_headers
        )

        response = await client.get(
            f"/clients/{cliente['id']}/service-requests", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["total"] == 1

    async def test_nao_atrapalha_as_rotas_de_clientes(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)

        response = await client.get(f"/clients/{cliente['id']}", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["id"] == cliente["id"]


class TestClientDeletion:
    async def test_excluir_cliente_com_solicitacao_devolve_409(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)
        await create_service_request(client, auth_headers, cliente["id"])

        response = await client.delete(
            f"/clients/{cliente['id']}", headers=auth_headers
        )

        assert response.status_code == 409
        assert response.json()["code"] == "conflict"

    async def test_excluir_cliente_sem_solicitacao_continua_funcionando(
        self, client: AsyncClient, auth_headers
    ) -> None:
        cliente = await create_client(client, auth_headers)

        response = await client.delete(
            f"/clients/{cliente['id']}", headers=auth_headers
        )

        assert response.status_code == 204
