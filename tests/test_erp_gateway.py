import httpx
import pytest
from app.erp_gateway.base import Factura
from app.erp_gateway.mock import MockERPGateway

@pytest.mark.asyncio
async def test_facturas_pendientes_calls_erp_with_token():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("authorization")
        return httpx.Response(200, json=[
            {"id": "F-1", "cliente": "ACME", "total": 100.0,
             "vencimiento": "2026-07-01", "pagada": False},
        ])

    transport = httpx.MockTransport(handler)
    gw = MockERPGateway(base_url="http://erp", transport=transport)
    facturas = await gw.facturas_pendientes(token="tok-123")

    assert captured["auth"] == "Bearer tok-123"
    assert "pagada=0" in captured["url"]
    assert facturas == [Factura(id="F-1", cliente="ACME", total=100.0,
                                vencimiento="2026-07-01", pagada=False)]
