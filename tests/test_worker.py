import uuid
import pytest
from app.documentos import worker as worker_mod

def test_worker_settings_registers_task():
    names = [getattr(f, "__name__", getattr(f, "name", None)) for f in worker_mod.WorkerSettings.functions]
    assert "process_document" in names

@pytest.mark.asyncio
async def test_process_document_invokes_indexing(monkeypatch):
    called = {}
    async def fake_index(session, document_id, *, storage, embedder, vector_store):
        called["document_id"] = document_id
        return 3
    monkeypatch.setattr(worker_mod, "index_document", fake_index)
    # make the session/deps cheap fakes
    class _CM:
        async def __aenter__(self): return "SESSION"
        async def __aexit__(self, *a): return False
    monkeypatch.setattr(worker_mod, "async_session_maker", lambda: _CM())
    monkeypatch.setattr(worker_mod, "get_storage", lambda: "STORAGE")
    monkeypatch.setattr(worker_mod, "get_embedder", lambda: "EMBEDDER")
    class _VS:
        def ensure_collection(self): pass
    monkeypatch.setattr(worker_mod, "get_vector_store", lambda: _VS())

    doc_id = str(uuid.uuid4())
    await worker_mod.process_document({}, doc_id)
    assert called["document_id"] == uuid.UUID(doc_id)
