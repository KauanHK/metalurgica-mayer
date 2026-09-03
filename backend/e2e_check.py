"""CRUD-piloto de ponta a ponta contra o PostgreSQL real."""
import asyncio
from httpx import ASGITransport, AsyncClient
from app.core.db.session import db
from app.main import app

async def main() -> None:
    db.init()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t/api") as c:
        r = await c.get("/health"); print(f"1. health           -> {r.status_code} {r.json()}")

        novo = {"name": "Construtora Alvorada Ltda", "document": "12.345.678/0001-95",
                "phone": "47988887777", "email": "contato@alvorada.com.br",
                "zip_code": "89108000", "street": "Rua das Palmeiras", "number": "1200",
                "neighborhood": "Centro", "city": "Massaranduba", "state": "sc",
                "notes": "Cliente recorrente de estruturas metálicas."}
        r = await c.post("/clients", json=novo); cid = r.json()["id"]
        j = r.json()
        print(f"2. criar            -> {r.status_code} doc={j['document']} tipo={j['document_type']} uf={j['state']}")

        r = await c.post("/clients", json={"name": "Outra", "document": "12345678000195"})
        print(f"3. doc duplicado    -> {r.status_code} {r.json()['code']}: {r.json()['message']}")

        for i in range(1, 4):
            await c.post("/clients", json={"name": f"Metalvale {i}", "is_active": i != 3})

        r = await c.get("/clients?page=1&page_size=2"); j = r.json()
        print(f"4. paginar          -> total={j['total']} paginas={j['total_pages']} nesta={len(j['data'])}")
        r = await c.get("/clients?search=alvorada")
        print(f"5. buscar 'alvorada'-> {r.json()['total']} resultado(s): {r.json()['data'][0]['name']}")
        r = await c.get("/clients?search=12345678")
        print(f"6. buscar por doc   -> {r.json()['total']} resultado(s)")
        r = await c.get("/clients?is_active=false")
        print(f"7. filtrar inativos -> {r.json()['total']} resultado(s)")

        r = await c.patch(f"/clients/{cid}", json={"phone": "4733334444"})
        j = r.json()
        print(f"8. PATCH parcial    -> {r.status_code} phone={j['phone']} name intacto={j['name']!r}")

        r = await c.get(f"/clients/{cid}")
        print(f"9. ler de volta     -> {r.status_code} {r.json()['phone']} (persistiu no banco)")

        r = await c.delete(f"/clients/{cid}"); print(f"10. excluir         -> {r.status_code}")
        r = await c.get(f"/clients/{cid}"); print(f"11. reconsultar     -> {r.status_code} {r.json()['code']}")
    await db.close()

asyncio.run(main())
