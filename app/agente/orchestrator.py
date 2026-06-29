from pydantic import BaseModel
from app.agente.provider import LLMMessage, LLMProvider
from app.agente.tools.base import ToolContext
from app.agente.tools.registry import ToolRegistry
from app.auth.roles import Role

SYSTEM_PROMPT = (
    "Eres el asistente de IDLED. Responde en español, de forma clara y honesta. "
    "No inventes datos: si necesitas información de facturas, stock, clientes o pedidos, "
    "usa las herramientas disponibles. Si no tienes una herramienta o permiso para algo, "
    "dilo claramente. Distingue entre información y acciones: en esta fase solo consultas, "
    "nunca modificas datos."
)

class AgentRun(BaseModel):
    text: str
    tools_used: list[str]

class AgentOrchestrator:
    def __init__(
        self,
        provider: LLMProvider,
        registry: ToolRegistry,
        max_tool_rounds: int = 4,
    ):
        self._provider = provider
        self._registry = registry
        self._max_rounds = max_tool_rounds

    async def run(
        self, user_message: str, history: list[LLMMessage], role: Role, ctx: ToolContext
    ) -> AgentRun:
        specs = self._registry.specs_for_role(role)
        allowed = {t.name for t in self._registry.for_role(role)}
        messages: list[LLMMessage] = [LLMMessage(role="system", content=SYSTEM_PROMPT)]
        messages.extend(history)
        messages.append(LLMMessage(role="user", content=user_message))

        tools_used: list[str] = []
        for _ in range(self._max_rounds):
            result = await self._provider.complete(messages, tools=specs)
            if not result.tool_calls:
                return AgentRun(text=result.text, tools_used=tools_used)
            # assistant turn that requested tools
            messages.append(LLMMessage(role="assistant", content=result.text or "", tool_calls=result.tool_calls))
            for call in result.tool_calls:
                tool = self._registry.get(call.name)
                if tool is None or call.name not in allowed:
                    output = f"Herramienta no disponible: {call.name}"
                else:
                    output = await tool.handler(ctx, call.arguments)
                    tools_used.append(call.name)
                messages.append(
                    LLMMessage(role="tool", content=output, tool_call_id=call.id, name=call.name)
                )
        # rounds exhausted: one final answer with no tools
        final = await self._provider.complete(messages, tools=None)
        return AgentRun(text=final.text, tools_used=tools_used)
