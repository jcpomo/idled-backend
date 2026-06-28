from app.agente.provider import LLMMessage, LLMToolSpec, ToolCall, LLMResult

def test_llmmessage_defaults():
    m = LLMMessage(role="user", content="hola")
    assert m.tool_call_id is None and m.name is None

def test_llmresult_defaults_empty():
    r = LLMResult()
    assert r.text == "" and r.tool_calls == []

def test_toolcall_shape():
    tc = ToolCall(id="c1", name="facturas_pendientes", arguments={"x": 1})
    assert tc.arguments == {"x": 1}

def test_tooltspec_shape():
    s = LLMToolSpec(name="t", description="d", parameters={"type": "object"})
    assert s.parameters["type"] == "object"
