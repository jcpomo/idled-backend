import pytest
from app.agente.provider import LLMMessage, LLMResult, ToolCall
from app.agente.fake_provider import FakeLLMProvider
from app.agente.orchestrator import AgentOrchestrator
from app.agente.tools.base import Tool, ToolContext
from app.agente.tools.registry import ToolRegistry
from app.auth.roles import Role
from app.erp_gateway.base import ERPGateway, Factura

class StubERP(ERPGateway):
    async def facturas_pendientes(self, token):
        return [Factura(id="F-9", cliente="X", total=5.0, vencimiento="2026-07-01", pagada=False)]
    async def stock_articulo(self, token, referencia):
        return None

async def _facturas_handler(ctx, args):
    f = await ctx.erp.facturas_pendientes(ctx.token)
    return f"{len(f)} facturas"

def _registry():
    reg = ToolRegistry()
    reg.register(Tool(name="facturas_pendientes", description="d",
                      parameters={"type": "object", "properties": {}},
                      permission="facturas:read", handler=_facturas_handler))
    return reg

def _ctx():
    return ToolContext(token="tok", erp=StubERP(), user_external_id="ext-1")

@pytest.mark.asyncio
async def test_run_uses_tool_then_answers():
    # 1st call -> tool_call; 2nd call -> final text
    provider = FakeLLMProvider(scripted_results=[
        LLMResult(tool_calls=[ToolCall(id="c1", name="facturas_pendientes", arguments={})]),
        LLMResult(text="Tienes 1 factura pendiente."),
    ])
    orch = AgentOrchestrator(provider=provider, registry=_registry())
    run = await orch.run("¿facturas pendientes?", history=[], role=Role.ADMINISTRACION, ctx=_ctx())
    assert run.text == "Tienes 1 factura pendiente."
    assert run.tools_used == ["facturas_pendientes"]

@pytest.mark.asyncio
async def test_run_no_tool_answers_directly():
    provider = FakeLLMProvider(scripted_results=[LLMResult(text="Hola, ¿en qué ayudo?")])
    orch = AgentOrchestrator(provider=provider, registry=_registry())
    run = await orch.run("hola", history=[], role=Role.LECTURA, ctx=_ctx())
    assert run.text == "Hola, ¿en qué ayudo?"
    assert run.tools_used == []

@pytest.mark.asyncio
async def test_role_without_permission_gets_no_facturas_tool():
    # produccion no tiene facturas:read -> el spec de tools pasado al modelo va vacío
    provider = FakeLLMProvider(scripted_results=[LLMResult(text="No tengo acceso a eso.")])
    orch = AgentOrchestrator(provider=provider, registry=_registry())
    await orch.run("¿facturas?", history=[], role=Role.PRODUCCION, ctx=_ctx())
    _, tools_arg = provider.complete_calls[0]
    assert tools_arg == []

@pytest.mark.asyncio
async def test_max_rounds_exhausted_returns_final_answer():
    # model keeps asking for the tool; with max_tool_rounds=1 the loop runs once,
    # then a final tools=None completion produces the answer.
    provider = FakeLLMProvider(scripted_results=[
        LLMResult(tool_calls=[ToolCall(id="c1", name="facturas_pendientes", arguments={})]),
        LLMResult(text="No puedo seguir."),
    ])
    orch = AgentOrchestrator(provider=provider, registry=_registry(), max_tool_rounds=1)
    run = await orch.run("loop", history=[], role=Role.ADMINISTRACION, ctx=_ctx())
    assert run.text == "No puedo seguir."

@pytest.mark.asyncio
async def test_disallowed_tool_call_is_not_executed():
    # produccion lacks facturas:read; even if the model returns a tool_call for it,
    # the orchestrator must NOT execute it (tools_used stays empty).
    provider = FakeLLMProvider(scripted_results=[
        LLMResult(tool_calls=[ToolCall(id="c1", name="facturas_pendientes", arguments={})]),
        LLMResult(text="No tengo acceso a esa herramienta."),
    ])
    orch = AgentOrchestrator(provider=provider, registry=_registry())
    run = await orch.run("¿facturas?", history=[], role=Role.PRODUCCION, ctx=_ctx())
    assert run.tools_used == []
    assert run.text == "No tengo acceso a esa herramienta."
