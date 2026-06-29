import pytest
from app.documentos.openai_embedder import OpenAIEmbedder

class _Emb:
    def __init__(self, vec): self.embedding = vec

class _Resp:
    def __init__(self, vecs): self.data = [_Emb(v) for v in vecs]

class FakeOpenAIClient:
    def __init__(self, vecs):
        self._vecs = vecs
        self.captured = {}
        self.embeddings = self
    async def create(self, **kwargs):
        self.captured = kwargs
        return _Resp(self._vecs)

@pytest.mark.asyncio
async def test_openai_embedder_maps_response():
    client = FakeOpenAIClient([[0.1, 0.2], [0.3, 0.4]])
    emb = OpenAIEmbedder(model="text-embedding-3-large", api_key="x", dim=3072, client=client)
    out = await emb.embed(["a", "b"])
    assert out == [[0.1, 0.2], [0.3, 0.4]]
    assert client.captured["model"] == "text-embedding-3-large"
    assert client.captured["input"] == ["a", "b"]
    assert emb.dim == 3072
