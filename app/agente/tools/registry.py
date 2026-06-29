from app.agente.provider import LLMToolSpec
from app.agente.tools.base import Tool
from app.auth.roles import Role, has_permission

class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def for_role(self, role: Role) -> list[Tool]:
        return [t for t in self._tools.values() if has_permission(role, t.permission)]

    def specs_for_role(self, role: Role) -> list[LLMToolSpec]:
        return [t.to_spec() for t in self.for_role(role)]

def build_default_registry() -> "ToolRegistry":
    from app.agente.tools.erp_tools import build_factura_tool, build_stock_tool
    from app.documentos.tools import build_buscar_documentos_tool
    from app.documentos.deps import get_embedder, get_vector_store
    reg = ToolRegistry()
    reg.register(build_factura_tool())
    reg.register(build_stock_tool())
    reg.register(build_buscar_documentos_tool(embedder=get_embedder(), vector_store=get_vector_store()))
    return reg
