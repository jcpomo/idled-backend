import json
import pytest
from app.agente.provider import LLMMessage, LLMToolSpec
from app.agente.openai_provider import OpenAIProvider

class _Msg:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []

class _ToolCall:
    def __init__(self, id, name, arguments):
        self.id = id
        self.type = "function"
        self.function = type("F", (), {"name": name, "arguments": json.dumps(arguments)})

class _Choice:
    def __init__(self, message): self.message = message

class _Resp:
    def __init__(self, message): self.choices = [_Choice(message)]

class FakeOpenAIClient:
    def __init__(self, response):
        self._response = response
        self.captured = {}
        self.chat = type("C", (), {"completions": self})()
    async def create(self, **kwargs):
        self.captured = kwargs
        return self._response

@pytest.mark.asyncio
async def test_complete_parses_tool_calls():
    resp = _Resp(_Msg(tool_calls=[_ToolCall("c1", "stock_articulo", {"referencia": "R1"})]))
    client = FakeOpenAIClient(resp)
    p = OpenAIProvider(model="gpt-4o", api_key="x", client=client)
    result = await p.complete(
        [LLMMessage(role="user", content="stock de R1")],
        tools=[LLMToolSpec(name="stock_articulo", description="d", parameters={"type": "object"})],
    )
    assert result.tool_calls[0].name == "stock_articulo"
    assert result.tool_calls[0].arguments == {"referencia": "R1"}
    # tradujo la tool al formato OpenAI (type=function)
    assert client.captured["tools"][0]["type"] == "function"
    assert client.captured["model"] == "gpt-4o"

@pytest.mark.asyncio
async def test_complete_plain_text():
    client = FakeOpenAIClient(_Resp(_Msg(content="hola")))
    p = OpenAIProvider(model="gpt-4o-mini", api_key="x", client=client)
    result = await p.complete([LLMMessage(role="user", content="hola")])
    assert result.text == "hola" and result.tool_calls == []
