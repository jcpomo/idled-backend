def test_documentos_settings_defaults(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    from app.core.config import get_settings
    get_settings.cache_clear()
    s = get_settings()
    assert s.embed_dim == 3072
    assert s.model_embed == "text-embedding-3-large"
    assert s.qdrant_collection == "documents"
    assert s.documents_bucket == "documents"

def test_embed_dim_overridable(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("EMBED_DIM", "1536")
    from app.core.config import get_settings
    get_settings.cache_clear()
    assert get_settings().embed_dim == 1536
