import jwt as pyjwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from app.auth.dependencies import get_current_user, require_permission
from app.auth.models import User
from app.core.db import get_session

SECRET = "test-secret"

def _token(role="administracion"):
    return pyjwt.encode({"sub": "ext-1", "role": role, "name": "Z"}, SECRET, algorithm="HS256")

@pytest.fixture
def app_client(session, monkeypatch):
    monkeypatch.setenv("JWT_SECRET", SECRET)
    from app.core.config import get_settings
    get_settings.cache_clear()

    app = FastAPI()

    async def _override_session():
        yield session

    app.dependency_overrides[get_session] = _override_session

    @app.get("/me")
    async def me(user: User = Depends(get_current_user)):
        return {"external_id": user.external_id, "role": user.role}

    @app.get("/facturas", dependencies=[Depends(require_permission("facturas:read"))])
    async def facturas():
        return {"ok": True}

    return TestClient(app)

def test_me_returns_user(app_client):
    r = app_client.get("/me", headers={"Authorization": f"Bearer {_token()}"})
    assert r.status_code == 200
    assert r.json()["external_id"] == "ext-1"

def test_missing_token_401(app_client):
    assert app_client.get("/me").status_code == 401

def test_permission_denied_403(app_client):
    r = app_client.get("/facturas", headers={"Authorization": f"Bearer {_token(role='produccion')}"})
    assert r.status_code == 403

def test_permission_granted(app_client):
    r = app_client.get("/facturas", headers={"Authorization": f"Bearer {_token(role='administracion')}"})
    assert r.status_code == 200
