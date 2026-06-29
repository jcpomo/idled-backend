from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import get_settings
from app.documentos.embedder import Embedder
from app.documentos.openai_embedder import OpenAIEmbedder
from app.documentos.storage import S3Storage
from app.documentos.vector_store import VectorStore
from qdrant_client import QdrantClient

def get_storage() -> S3Storage:
    s = get_settings()
    return S3Storage(s.minio_endpoint, s.minio_access_key, s.minio_secret_key, s.documents_bucket)

def get_embedder() -> Embedder:
    s = get_settings()
    return OpenAIEmbedder(model=s.model_embed, api_key=s.openai_api_key, dim=s.embed_dim)

def get_vector_store() -> VectorStore:
    s = get_settings()
    # check_compatibility=False avoids an init-time network ping to Qdrant, so constructing
    # the store (e.g. while building the tool registry) is lazy and keeps tests hermetic.
    client = QdrantClient(url=s.qdrant_url, check_compatibility=False)
    return VectorStore(client=client, collection=s.qdrant_collection, dim=s.embed_dim)

async def enqueue_index_job(document_id) -> None:
    s = get_settings()
    pool = await create_pool(RedisSettings.from_dsn(s.redis_url))
    await pool.enqueue_job("process_document", str(document_id))
    await pool.aclose()
