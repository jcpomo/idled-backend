import jwt as pyjwt
import pytest
import httpx
from app.core.db import get_session

SECRET = "test-secret-which-is-long-enough-to-avoid-pyjwt-key-warnings-0123456789"

def _token(sub="ext-7", role="administracion"):
    return pyjwt.encode({"sub": sub, "role": role, "name": "Q"}, SECRET, algorithm="HS256")

@pytest.fixture
def client(session, monkeypatch):
    monkeypatch.setenv("JWT_SECRET", SECRET)
    from app.core.config import get_settings
    get_settings.cache_clear()
    from app.main import app

    async def _override_session():
        yield session

    app.dependency_overrides[get_session] = _override_session
    transport = httpx.ASGITransport(app=app)
    yield httpx.AsyncClient(transport=transport, base_url="http://test")
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_project_crud_and_nested_tasks(client):
    async with client as ac:
        h = {"Authorization": f"Bearer {_token()}"}
        # create + list
        r = await ac.post("/api/projects", json={"name": "Serie X"}, headers=h)
        assert r.status_code == 200
        pid = r.json()["id"]
        lst = await ac.get("/api/projects", headers=h)
        assert any(p["name"] == "Serie X" for p in lst.json())
        # nested task create + list
        rt = await ac.post(f"/api/projects/{pid}/tasks",
                           json={"title": "Estudio viabilidad", "task_type": "PPTO"}, headers=h)
        assert rt.status_code == 200 and rt.json()["status"] == "open"
        tasks = await ac.get(f"/api/projects/{pid}/tasks", headers=h)
        assert [t["title"] for t in tasks.json()] == ["Estudio viabilidad"]
        # rename + delete
        assert (await ac.patch(f"/api/projects/{pid}", json={"name": "Serie Y"}, headers=h)).status_code == 200
        assert (await ac.delete(f"/api/projects/{pid}", headers=h)).json()["deleted"] is True

@pytest.mark.asyncio
async def test_other_user_gets_404(client):
    async with client as ac:
        pid = (await ac.post("/api/projects", json={"name": "P"},
                             headers={"Authorization": f"Bearer {_token(sub='owner')}"})).json()["id"]
        r = await ac.get(f"/api/projects/{pid}/tasks",
                         headers={"Authorization": f"Bearer {_token(sub='intruder')}"})
        assert r.status_code == 404

@pytest.mark.asyncio
async def test_invalid_status_422(client):
    async with client as ac:
        h = {"Authorization": f"Bearer {_token()}"}
        pid = (await ac.post("/api/projects", json={"name": "P"}, headers=h)).json()["id"]
        r = await ac.post(f"/api/projects/{pid}/tasks",
                          json={"title": "x", "status": "todo"}, headers=h)
        assert r.status_code == 422

@pytest.mark.asyncio
async def test_requires_auth(client):
    async with client as ac:
        assert (await ac.get("/api/projects")).status_code == 401
