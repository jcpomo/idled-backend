import httpx
import jwt as pyjwt
import pytest
from sqlalchemy import select
from app.audit.models import AuditLog
from app.core.db import get_session
from app.erp_gateway.dependencies import get_erp_gateway
from app.erp_gateway.base import Factura, ERPGateway

SECRET = "test-secret-which-is-long-enough-to-avoid-pyjwt-key-warnings-0123456789"

def _token(role="administracion"):
    return pyjwt.encode({"sub": "ext-7", "role": role, "name": "Q"}, SECRET, algorithm="HS256")

class FakeGateway(ERPGateway):
    async def facturas_pendientes(self, token: str) -> list[Factura]:
        return [Factura(id="F-9", cliente="X", total=5.0, vencimiento="2026-07-01", pagada=False)]

@pytest.fixture
def app_with_overrides(session, monkeypatch):
    monkeypatch.setenv("JWT_SECRET", SECRET)
    from app.core.config import get_settings
    get_settings.cache_clear()
    from app.main import app

    async def _override_session():
        yield session

    app.dependency_overrides[get_session] = _override_session
    app.dependency_overrides[get_erp_gateway] = lambda: FakeGateway()
    yield app
    app.dependency_overrides.clear()

async def test_facturas_endpoint_returns_and_audits(app_with_overrides, session):
    transport = httpx.ASGITransport(app=app_with_overrides)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/erp/facturas-pendientes",
                         headers={"Authorization": f"Bearer {_token()}"})
    assert r.status_code == 200
    assert r.json()[0]["id"] == "F-9"
    rows = (await session.execute(select(AuditLog))).scalars().all()
    assert any(row.action == "facturas_pendientes" for row in rows)

async def test_facturas_endpoint_forbidden_for_produccion(app_with_overrides):
    transport = httpx.ASGITransport(app=app_with_overrides)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/erp/facturas-pendientes",
                         headers={"Authorization": f"Bearer {_token(role='produccion')}"})
    assert r.status_code == 403
