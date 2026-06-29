import uuid
from arq.connections import RedisSettings
from app.core.config import get_settings
from app.core.db import async_session_maker
from app.documentos.deps import get_embedder, get_storage, get_vector_store
from app.documentos.indexing import index_document

async def process_document(ctx, document_id: str) -> int:
    storage = get_storage()
    embedder = get_embedder()
    vector_store = get_vector_store()
    vector_store.ensure_collection()
    async with async_session_maker() as session:
        return await index_document(
            session, uuid.UUID(document_id),
            storage=storage, embedder=embedder, vector_store=vector_store,
        )

class WorkerSettings:
    functions = [process_document]
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
