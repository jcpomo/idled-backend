import httpx
from app.erp_gateway.base import ERPGateway, Factura

class MockERPGateway(ERPGateway):
    def __init__(self, base_url: str, transport: httpx.BaseTransport | None = None):
        self._base_url = base_url.rstrip("/")
        self._transport = transport

    async def facturas_pendientes(self, token: str) -> list[Factura]:
        async with httpx.AsyncClient(transport=self._transport) as client:
            resp = await client.get(
                f"{self._base_url}/api/facturas",
                params={"pagada": 0},
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            return [Factura(**row) for row in resp.json()]

    async def stock_articulo(self, token: str, referencia: str):
        from app.erp_gateway.base import Articulo
        async with httpx.AsyncClient(transport=self._transport) as client:
            resp = await client.get(
                f"{self._base_url}/api/stock",
                params={"referencia": referencia},
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            data = resp.json()
            return Articulo(**data) if data else None
