from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from pydantic import BaseModel

class LLMMessage(BaseModel):
    role: str
    content: str
    tool_call_id: str | None = None
    name: str | None = None

class LLMToolSpec(BaseModel):
    name: str
    description: str
    parameters: dict

class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict

class LLMResult(BaseModel):
    text: str = ""
    tool_calls: list[ToolCall] = []

class LLMProvider(ABC):
    @abstractmethod
    async def complete(
        self, messages: list[LLMMessage], tools: list[LLMToolSpec] | None = None
    ) -> LLMResult: ...

    @abstractmethod
    def stream_text(self, messages: list[LLMMessage]) -> AsyncIterator[str]: ...
