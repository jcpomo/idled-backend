import pytest
from qdrant_client import QdrantClient
from app.documentos.tools import build_buscar_documentos_tool
from app.documentos.embedder import FakeEmbedder
from app.documentos.vector_store import VectorStore, DocChunk
from app.agente.tools.base import ToolContext

async def _seeded():
    emb = FakeEmbedder(dim=4)
    vs = VectorStore(client=QdrantClient(location=":memory:"), collection="documents", dim=4)
    vs.ensure_collection()
    vec = (await emb.embed(["factura de ACME por 1200"]))[0]
    vs.upsert([DocChunk(id="00000000-0000-0000-0000-000000000001", vector=vec,
                        document_id="d1", user_external_id="ext-1", chunk_index=0,
                        text="factura de ACME por 1200")])
    return emb, vs

@pytest.mark.asyncio
async def test_tool_returns_user_scoped_results():
    emb, vs = await _seeded()
    tool = build_buscar_documentos_tool(embedder=emb, vector_store=vs)
    assert tool.name == "buscar_en_documentos"
    assert tool.permission == "documentos:read"
    ctx = ToolContext(token="t", erp=None, user_external_id="ext-1")
    out = await tool.handler(ctx, {"consulta": "factura ACME"})
    assert "ACME" in out

@pytest.mark.asyncio
async def test_tool_other_user_gets_no_results():
    emb, vs = await _seeded()
    tool = build_buscar_documentos_tool(embedder=emb, vector_store=vs)
    ctx = ToolContext(token="t", erp=None, user_external_id="ext-OTHER")
    out = await tool.handler(ctx, {"consulta": "factura ACME"})
    assert "sin resultados" in out.lower()
