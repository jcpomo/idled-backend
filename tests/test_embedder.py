import pytest
from app.documentos.embedder import FakeEmbedder

@pytest.mark.asyncio
async def test_fake_embedder_shape_and_determinism():
    emb = FakeEmbedder(dim=8)
    v1 = await emb.embed(["hola", "mundo"])
    v2 = await emb.embed(["hola"])
    assert len(v1) == 2 and all(len(v) == 8 for v in v1)
    assert v1[0] == v2[0]            # deterministic per text
    assert emb.dim == 8
    assert emb.embed_calls == [["hola", "mundo"], ["hola"]]
