import pytest
from app.documentos.chunking import chunk_text

def test_short_text_one_chunk():
    assert chunk_text("hola", size=800) == ["hola"]

def test_empty_is_no_chunks():
    assert chunk_text("   ") == []

def test_splits_with_overlap():
    text = "abcdefghij"  # 10 chars
    chunks = chunk_text(text, size=4, overlap=1)
    # step = size - overlap = 3 -> starts at 0,3,6,9
    assert chunks == ["abcd", "defg", "ghij", "j"]

def test_overlap_ge_size_raises():
    with pytest.raises(ValueError):
        chunk_text("abc", size=2, overlap=2)
