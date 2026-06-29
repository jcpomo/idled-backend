import hashlib
from abc import ABC, abstractmethod

class Embedder(ABC):
    @property
    @abstractmethod
    def dim(self) -> int: ...

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]: ...

class FakeEmbedder(Embedder):
    def __init__(self, dim: int = 8):
        self._dim = dim
        self.embed_calls: list[list[str]] = []

    @property
    def dim(self) -> int:
        return self._dim

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.embed_calls.append(list(texts))
        vectors: list[list[float]] = []
        for t in texts:
            digest = hashlib.sha256(t.encode("utf-8")).digest()
            vectors.append([digest[i % len(digest)] / 255.0 for i in range(self._dim)])
        return vectors
