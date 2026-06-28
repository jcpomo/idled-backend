import os
import json
import httpx
import pytest

API = os.getenv("E2E_API_URL", "http://localhost:8000")
ERP = os.getenv("E2E_ERP_URL", "http://localhost:8080")

@pytest.mark.live
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="needs OPENAI_API_KEY")
def test_chat_live_answers():
    token = httpx.post(f"{ERP}/api/login", json={"email": "ana@idled.test"}, timeout=10).json()["token"]
    r = httpx.post(f"{API}/api/chat",
                   json={"message": "¿Qué facturas están pendientes de cobro?", "conversation_id": None},
                   headers={"Authorization": f"Bearer {token}"}, timeout=60)
    assert r.status_code == 200
    assert "F-1001" in r.text or "factura" in r.text.lower()
