import pytest
from app.agente.provider import LLMMessage, LLMResult, ToolCall, LLMToolSpec
from app.agente.fake_provider import FakeLLMProvider

@pytest.mark.asyncio
async def test_complete_returns_scripted_in_order():
    p = FakeLLMProvider(scripted_results=[
        LLMResult(tool_calls=[ToolCall(id="c1", name="t", arguments={})]),
        LLMResult(text="respuesta final"),
    ])
    r1 = await p.complete([LLMMessage(role="user", content="x")], tools=[])
    r2 = await p.complete([LLMMessage(role="user", content="x")])
    assert r1.tool_calls[0].name == "t"
    assert r2.text == "respuesta final"
    assert len(p.complete_calls) == 2

@pytest.mark.asyncio
async def test_stream_text_yields_chunks():
    p = FakeLLMProvider(scripted_results=[LLMResult(text="hola mundo")],
                        stream_chunks=["ho", "la", " mundo"])
    out = "".join([c async for c in p.stream_text([LLMMessage(role="user", content="x")])])
    assert out == "hola mundo"
