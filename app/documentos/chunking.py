def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    if overlap >= size:
        raise ValueError("overlap debe ser menor que size")
    stripped = text.strip()
    if not stripped:
        return []
    step = size - overlap
    chunks: list[str] = []
    for start in range(0, len(stripped), step):
        chunk = stripped[start:start + size]
        if chunk:
            chunks.append(chunk)
    return chunks
