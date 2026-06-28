from collections.abc import AsyncIterator
from app.agente.provider import LLMMessage, LLMProvider, LLMResult, LLMToolSpec

class FakeLLMProvider(LLMProvider):
    def __init__(
        self,
        scripted_results: list[LLMResult],
        stream_chunks: list[str] | None = None,
    ):
        self._results = list(scripted_results)
        self._stream_chunks = stream_chunks
        self.complete_calls: list[tuple[list[LLMMessage], list[LLMToolSpec] | None]] = []

    async def complete(
        self, messages: list[LLMMessage], tools: list[LLMToolSpec] | None = None
    ) -> LLMResult:
        self.complete_calls.append((messages, tools))
        return self._results.pop(0)

    async def stream_text(self, messages: list[LLMMessage]) -> AsyncIterator[str]:
        chunks = self._stream_chunks
        if chunks is None:
            chunks = [self._results[-1].text] if self._results else [""]
        for c in chunks:
            yield c
