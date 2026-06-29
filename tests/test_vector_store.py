import pytest
from qdrant_client import QdrantClient
from app.documentos.vector_store import VectorStore, DocChunk

def _store():
    client = QdrantClient(location=":memory:")
    vs = VectorStore(client=client, collection="documents", dim=4)
    vs.ensure_collection()
    return vs

@pytest.mark.asyncio
async def test_upsert_and_search_filters_by_user():
    vs = _store()
    vs.upsert([
        DocChunk(id="00000000-0000-0000-0000-000000000001", vector=[1, 0, 0, 0],
                 document_id="d1", user_external_id="ext-1", chunk_index=0, text="factura ACME"),
        DocChunk(id="00000000-0000-0000-0000-000000000002", vector=[0, 1, 0, 0],
                 document_id="d2", user_external_id="ext-2", chunk_index=0, text="oferta Globex"),
    ])
    hits = vs.search(vector=[1, 0, 0, 0], user_external_id="ext-1", top_k=5)
    assert [h.text for h in hits] == ["factura ACME"]   # ext-2's point excluded
    assert hits[0].document_id == "d1"

def test_ensure_collection_idempotent():
    vs = _store()
    vs.ensure_collection()  # second call must not raise
