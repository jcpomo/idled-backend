import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.documentos.chunking import chunk_text
from app.documentos.embedder import Embedder
from app.documentos.extract import extract_text
from app.documentos.service import get_document, set_status
from app.documentos.storage import ObjectStorage
from app.documentos.vector_store import DocChunk, VectorStore

_NAMESPACE = uuid.UUID("11111111-1111-1111-1111-111111111111")

async def index_document(
    session: AsyncSession, document_id: uuid.UUID, *,
    storage: ObjectStorage, embedder: Embedder, vector_store: VectorStore,
) -> int:
    doc = await get_document(session, document_id)
    if doc is None:
        raise ValueError(f"Documento no encontrado: {document_id}")
    try:
        await set_status(session, document_id, "processing")
        raw = storage.get(doc.storage_key)
        text = extract_text(raw, doc.content_type)
        chunks = chunk_text(text)
        if chunks:
            vectors = await embedder.embed(chunks)
            points = [
                DocChunk(
                    id=str(uuid.uuid5(_NAMESPACE, f"{document_id}-{i}")),
                    vector=vectors[i], document_id=str(document_id),
                    user_external_id=doc.user_external_id, chunk_index=i, text=chunks[i],
                )
                for i in range(len(chunks))
            ]
            vector_store.upsert(points)
        await set_status(session, document_id, "indexed")
        return len(chunks)
    except Exception as exc:
        await set_status(session, document_id, "failed", error=str(exc))
        raise
