from app.core.config import Settings

def test_settings_read_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
    monkeypatch.setenv("JWT_SECRET", "shhh")
    monkeypatch.setenv("ERP_BASE_URL", "http://mini-laravel")
    monkeypatch.setenv("QDRANT_URL", "http://qdrant:6333")
    monkeypatch.setenv("REDIS_URL", "redis://redis:6379")
    s = Settings()
    assert s.jwt_secret == "shhh"
    assert s.jwt_algorithm == "HS256"
    assert s.erp_base_url == "http://mini-laravel"
