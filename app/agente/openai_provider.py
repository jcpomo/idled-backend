import json
from collections.abc import AsyncIterator
from openai import AsyncOpenAI
from app.agente.provider import LLMMessage, LLMProvider, LLMResult, LLMToolSpec, ToolCall

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str, api_key: str, client=None):
        self._model = model
        self._client = client or AsyncOpenAI(api_key=api_key)

    def _to_openai_messages(self, messages: list[LLMMessage]) -> list[dict]:
        out = []
        for m in messages:
            d: dict = {"role": m.role, "content": m.content}
            if m.tool_call_id:
                d["tool_call_id"] = m.tool_call_id
            if m.name:
                d["name"] = m.name
            out.append(d)
        return out

    def _to_openai_tools(self, tools: list[LLMToolSpec] | None) -> list[dict] | None:
        if not tools:
            return None
        return [
            {"type": "function",
             "function": {"name": t.name, "description": t.description, "parameters": t.parameters}}
            for t in tools
        ]

    async def complete(
        self, messages: list[LLMMessage], tools: list[LLMToolSpec] | None = None
    ) -> LLMResult:
        kwargs: dict = {"model": self._model, "messages": self._to_openai_messages(messages)}
        oa_tools = self._to_openai_tools(tools)
        if oa_tools:
            kwargs["tools"] = oa_tools
        resp = await self._client.chat.completions.create(**kwargs)
        msg = resp.choices[0].message
        calls = [
            ToolCall(id=tc.id, name=tc.function.name, arguments=json.loads(tc.function.arguments or "{}"))
            for tc in (msg.tool_calls or [])
        ]
        return LLMResult(text=msg.content or "", tool_calls=calls)

    async def stream_text(self, messages: list[LLMMessage]) -> AsyncIterator[str]:
        stream = await self._client.chat.completions.create(
            model=self._model, messages=self._to_openai_messages(messages), stream=True
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
