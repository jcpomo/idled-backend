import jwt as pyjwt
import pytest
import httpx
from app.core.db import get_session

SECRET = "test-secret-which-is-long-enough-to-avoid-pyjwt-key-warnings-0123456789"

def _token(sub="ext-7"):
    return pyjwt.encode({"sub": sub, "role": "administracion", "name": "Q"}, SECRET, algorithm="HS256")

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

async def _make_task(ac, h):
    pid = (await ac.post("/api/projects", json={"name": "P"}, headers=h)).json()["id"]
    return (await ac.post(f"/api/projects/{pid}/tasks", json={"title": "a"}, headers=h)).json()["id"]

@pytest.mark.asyncio
async def test_update_move_delete(client):
    async with client as ac:
        h = {"Authorization": f"Bearer {_token()}"}
        tid = await _make_task(ac, h)
        # update
        ru = await ac.patch(f"/api/tasks/{tid}", json={"title": "b", "assignee": "ED"}, headers=h)
        assert ru.status_code == 200 and ru.json()["title"] == "b" and ru.json()["assignee"] == "ED"
        # move
        rm = await ac.post(f"/api/tasks/{tid}/move", json={"status": "done", "position": 0}, headers=h)
        assert rm.status_code == 200 and rm.json()["status"] == "done"
        # delete
        assert (await ac.delete(f"/api/tasks/{tid}", headers=h)).json()["deleted"] is True

@pytest.mark.asyncio
async def test_move_invalid_status_422(client):
    async with client as ac:
        h = {"Authorization": f"Bearer {_token()}"}
        tid = await _make_task(ac, h)
        r = await ac.post(f"/api/tasks/{tid}/move", json={"status": "todo", "position": 0}, headers=h)
        assert r.status_code == 422

@pytest.mark.asyncio
async def test_other_user_move_404(client):
    async with client as ac:
        tid = await _make_task(ac, {"Authorization": f"Bearer {_token(sub='owner')}"})
        r = await ac.post(f"/api/tasks/{tid}/move", json={"status": "done", "position": 0},
                          headers={"Authorization": f"Bearer {_token(sub='intruder')}"})
        assert r.status_code == 404
