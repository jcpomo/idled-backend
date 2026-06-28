import pytest
from app.agente.tools.base import ToolContext
from app.agente.tools.erp_tools import build_factura_tool, build_stock_tool
from app.erp_gateway.base import ERPGateway, Factura, Articulo

class StubERP(ERPGateway):
    async def facturas_pendientes(self, token: str) -> list[Factura]:
        return [Factura(id="F-1", cliente="ACME", total=100.0, vencimiento="2026-07-01", pagada=False)]
    async def stock_articulo(self, token: str, referencia: str):
        return Articulo(referencia=referencia, descripcion="Tornillo", stock=42) if referencia == "R1" else None

def _ctx():
    return ToolContext(token="tok", erp=StubERP(), user_external_id="ext-1")

@pytest.mark.asyncio
async def test_factura_tool_summarizes():
    tool = build_factura_tool()
    out = await tool.handler(_ctx(), {})
    assert "F-1" in out and "ACME" in out
    assert tool.permission == "facturas:read"

@pytest.mark.asyncio
async def test_stock_tool_found_and_missing():
    tool = build_stock_tool()
    found = await tool.handler(_ctx(), {"referencia": "R1"})
    missing = await tool.handler(_ctx(), {"referencia": "ZZ"})
    assert "42" in found and "Tornillo" in found
    assert "no encontrado" in missing.lower()
    assert tool.permission == "stock:read"
