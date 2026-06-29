from dataclasses import dataclass
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams,
)

@dataclass
class DocChunk:
    id: str
    vector: list[float]
    document_id: str
    user_external_id: str
    chunk_index: int
    text: str

@dataclass
class SearchHit:
    text: str
    document_id: str
    score: float

class VectorStore:
    def __init__(self, client: QdrantClient, collection: str, dim: int):
        self._client = client
        self._collection = collection
        self._dim = dim

    def ensure_collection(self) -> None:
        if not self._client.collection_exists(self._collection):
            self._client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(size=self._dim, distance=Distance.COSINE),
            )

    def upsert(self, chunks: list["DocChunk"]) -> None:
        points = [
            PointStruct(
                id=c.id, vector=c.vector,
                payload={
                    "document_id": c.document_id,
                    "user_external_id": c.user_external_id,
                    "chunk_index": c.chunk_index,
                    "text": c.text,
                },
            )
            for c in chunks
        ]
        if points:
            self._client.upsert(collection_name=self._collection, points=points)

    def search(self, vector: list[float], user_external_id: str, top_k: int = 5) -> list["SearchHit"]:
        flt = Filter(must=[FieldCondition(key="user_external_id", match=MatchValue(value=user_external_id))])
        results = self._client.query_points(
            collection_name=self._collection, query=vector,
            query_filter=flt, limit=top_k,
        ).points
        return [
            SearchHit(text=r.payload["text"], document_id=r.payload["document_id"], score=r.score)
            for r in results
        ]
