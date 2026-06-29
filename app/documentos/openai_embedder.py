from openai import AsyncOpenAI
from app.documentos.embedder import Embedder

class OpenAIEmbedder(Embedder):
    def __init__(self, model: str, api_key: str, dim: int, client=None):
        self._model = model
        self._dim = dim
        self._client = client or AsyncOpenAI(api_key=api_key)

    @property
    def dim(self) -> int:
        return self._dim

    async def embed(self, texts: list[str]) -> list[list[float]]:
        resp = await self._client.embeddings.create(model=self._model, input=texts)
        return [d.embedding for d in resp.data]
