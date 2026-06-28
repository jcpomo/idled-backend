from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from app.agente.provider import LLMToolSpec
from app.erp_gateway.base import ERPGateway

@dataclass
class ToolContext:
    token: str
    erp: ERPGateway
    user_external_id: str

@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    permission: str
    handler: Callable[["ToolContext", dict], Awaitable[str]]

    def to_spec(self) -> LLMToolSpec:
        return LLMToolSpec(name=self.name, description=self.description, parameters=self.parameters)
