from app.agente.tools.base import Tool, ToolContext
from app.agente.tools.registry import ToolRegistry
from app.auth.roles import Role

async def _noop(ctx, args):
    return "ok"

def _tool(name, permission):
    return Tool(name=name, description="d", parameters={"type": "object", "properties": {}},
                permission=permission, handler=_noop)

def test_for_role_filters_by_permission():
    reg = ToolRegistry()
    reg.register(_tool("facturas_pendientes", "facturas:read"))
    reg.register(_tool("ordenes", "ordenes:read"))
    admin_tools = {t.name for t in reg.for_role(Role.ADMIN)}
    prod_tools = {t.name for t in reg.for_role(Role.PRODUCCION)}
    assert admin_tools == {"facturas_pendientes", "ordenes"}
    assert prod_tools == {"ordenes"}            # produccion no tiene facturas:read

def test_get_and_specs():
    reg = ToolRegistry()
    reg.register(_tool("facturas_pendientes", "facturas:read"))
    assert reg.get("facturas_pendientes").name == "facturas_pendientes"
    assert reg.get("missing") is None
    specs = reg.specs_for_role(Role.ADMINISTRACION)
    assert specs[0].name == "facturas_pendientes"
