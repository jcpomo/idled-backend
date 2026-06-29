import pytest
from app.documentos.service import create_document, get_document
from app.documentos.indexing import index_document
from app.documentos.embedder import FakeEmbedder
from app.documentos.storage import FakeStorage
from app.documentos.vector_store import VectorStore
from qdrant_client import QdrantClient

@pytest.mark.asyncio
async def test_index_document_happy_path(session):
    storage = FakeStorage()
    storage.put("k/doc", "ACME factura 100\nGlobex oferta 200".encode(), "text/plain")
    doc = await create_document(session, "ext-1", "f.txt", "text/plain", "k/doc")

    embedder = FakeEmbedder(dim=4)
    vs = VectorStore(client=QdrantClient(location=":memory:"), collection="documents", dim=4)
    vs.ensure_collection()

    n = await index_document(session, doc.id, storage=storage, embedder=embedder, vector_store=vs)
    assert n >= 1
    refreshed = await get_document(session, doc.id)
    assert refreshed.status == "indexed"
    # the chunk is searchable and scoped to the user
    qv = (await embedder.embed(["factura"]))[0]
    hits = vs.search(vector=qv, user_external_id="ext-1", top_k=5)
    assert hits and hits[0].document_id == str(doc.id)

@pytest.mark.asyncio
async def test_index_document_marks_failed_on_bad_type(session):
    storage = FakeStorage()
    storage.put("k/bad", b"\x00", "image/png")
    doc = await create_document(session, "ext-1", "x.png", "image/png", "k/bad")
    vs = VectorStore(client=QdrantClient(location=":memory:"), collection="documents", dim=4)
    vs.ensure_collection()
    with pytest.raises(ValueError):
        await index_document(session, doc.id, storage=storage, embedder=FakeEmbedder(dim=4), vector_store=vs)
    refreshed = await get_document(session, doc.id)
    assert refreshed.status == "failed"
    assert refreshed.error
