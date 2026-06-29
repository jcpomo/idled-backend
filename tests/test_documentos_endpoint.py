import jwt as pyjwt
import pytest
import httpx
from sqlalchemy import select
from app.audit.models import AuditLog
from app.core.db import get_session
from app.documentos.api_deps import get_storage_dep, enqueue_dep  # see Step 4
from app.documentos.storage import FakeStorage

SECRET = "test-secret-which-is-long-enough-to-avoid-pyjwt-key-warnings-0123456789"

def _token(role="administracion"):
    return pyjwt.encode({"sub": "ext-7", "role": role, "name": "Q"}, SECRET, algorithm="HS256")

@pytest.fixture
def app_with_overrides(session, monkeypatch):
    monkeypatch.setenv("JWT_SECRET", SECRET)
    from app.core.config import get_settings
    get_settings.cache_clear()
    from app.main import app
    enqueued = []

    async def _override_session():
        yield session

    app.dependency_overrides[get_session] = _override_session
    app.dependency_overrides[get_storage_dep] = lambda: FakeStorage()
    async def _fake_enqueue(document_id): enqueued.append(str(document_id))
    app.dependency_overrides[enqueue_dep] = lambda: _fake_enqueue
    app.state._enqueued = enqueued
    yield app
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_upload_creates_document_enqueues_and_audits(app_with_overrides, session):
    transport = httpx.ASGITransport(app=app_with_overrides)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post(
            "/api/documentos",
            headers={"Authorization": f"Bearer {_token()}"},
            files={"file": ("f.txt", b"hola contenido", "text/plain")},
        )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "uploaded" and body["document_id"]
    assert app_with_overrides.state._enqueued == [body["document_id"]]
    rows = (await session.execute(select(AuditLog))).scalars().all()
    assert any(row.action == "document_upload" for row in rows)

@pytest.mark.asyncio
async def test_list_returns_user_documents(app_with_overrides):
    transport = httpx.ASGITransport(app=app_with_overrides)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/api/documentos", headers={"Authorization": f"Bearer {_token()}"},
                      files={"file": ("a.txt", b"x", "text/plain")})
        r = await ac.get("/api/documentos", headers={"Authorization": f"Bearer {_token()}"})
    assert r.status_code == 200
    assert any(d["filename"] == "a.txt" for d in r.json())

@pytest.mark.asyncio
async def test_upload_forbidden_for_lectura(app_with_overrides):
    transport = httpx.ASGITransport(app=app_with_overrides)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/documentos", headers={"Authorization": f"Bearer {_token(role='lectura')}"},
                          files={"file": ("a.txt", b"x", "text/plain")})
    assert r.status_code == 403
