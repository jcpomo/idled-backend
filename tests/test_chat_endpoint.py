import json
import jwt as pyjwt
import pytest
import httpx
from sqlalchemy import select
from app.audit.models import AuditLog
from app.core.db import get_session
from app.agente.provider import LLMResult, ToolCall
from app.agente.fake_provider import FakeLLMProvider
from app.erp_gateway.base import ERPGateway, Factura
from app.erp_gateway.dependencies import get_erp_gateway


class _FakeGateway(ERPGateway):
    async def facturas_pendientes(self, token: str):
        return [Factura(id="F-1001", cliente="ACME", total=10.0, vencimiento="2026-07-01", pagada=False)]
    async def stock_articulo(self, token: str, referencia: str):
        return None

SECRET = "test-secret-which-is-long-enough-to-avoid-pyjwt-key-warnings-0123456789"

def _token(role="administracion"):
    return pyjwt.encode({"sub": "ext-7", "role": role, "name": "Q"}, SECRET, algorithm="HS256")

@pytest.fixture
def app_with_overrides(session, monkeypatch):
    monkeypatch.setenv("JWT_SECRET", SECRET)
    from app.core.config import get_settings
    get_settings.cache_clear()
    from app.main import app
    from app.api.chat import get_orchestrator
    from app.agente.orchestrator import AgentOrchestrator
    from app.agente.tools.registry import build_default_registry

    async def _override_session():
        yield session

    def _fake_orchestrator():
        provider = FakeLLMProvider(scripted_results=[
            LLMResult(tool_calls=[ToolCall(id="c1", name="facturas_pendientes", arguments={})]),
            LLMResult(text="Tienes facturas pendientes."),
        ])
        return AgentOrchestrator(provider=provider, registry=build_default_registry())

    app.dependency_overrides[get_session] = _override_session
    app.dependency_overrides[get_orchestrator] = _fake_orchestrator
    app.dependency_overrides[get_erp_gateway] = lambda: _FakeGateway()
    yield app
    app.dependency_overrides.clear()

async def _post_chat(app, token, body):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        return await ac.post("/api/chat", json=body, headers={"Authorization": f"Bearer {token}"})

@pytest.mark.asyncio
async def test_chat_streams_and_persists_and_audits(app_with_overrides, session):
    r = await _post_chat(app_with_overrides, _token(), {"message": "¿facturas?", "conversation_id": None})
    assert r.status_code == 200
    body = r.text
    assert "Tienes facturas pendientes." in body
    assert '"type": "meta"' in body or '"type":"meta"' in body
    # auditoría
    rows = (await session.execute(select(AuditLog))).scalars().all()
    assert any(row.action == "chat_query" for row in rows)

@pytest.mark.asyncio
async def test_chat_requires_auth(app_with_overrides):
    transport = httpx.ASGITransport(app=app_with_overrides)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/chat", json={"message": "hola", "conversation_id": None})
    assert r.status_code == 401
