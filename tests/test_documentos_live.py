import os
import time
import httpx
import pytest

API = os.getenv("E2E_API_URL", "http://localhost:8000")
ERP = os.getenv("E2E_ERP_URL", "http://localhost:8080")

@pytest.mark.live
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="needs OPENAI_API_KEY")
def test_upload_index_and_query():
    token = httpx.post(f"{ERP}/api/login", json={"email": "ana@idled.test"}, timeout=10).json()["token"]
    h = {"Authorization": f"Bearer {token}"}
    content = b"El proyecto secreto se llama Colibri y su presupuesto es 48000 euros."
    up = httpx.post(f"{API}/api/documentos", headers=h,
                    files={"file": ("nota.txt", content, "text/plain")}, timeout=30)
    assert up.status_code == 200
    doc_id = up.json()["document_id"]

    deadline = time.time() + 60
    status = None
    while time.time() < deadline:
        docs = httpx.get(f"{API}/api/documentos", headers=h, timeout=10).json()
        status = next((d["status"] for d in docs if d["id"] == doc_id), None)
        if status in ("indexed", "failed"):
            break
        time.sleep(2)
    assert status == "indexed", f"document status was {status}"

    chat = httpx.post(f"{API}/api/chat", headers=h,
                      json={"message": "¿Cómo se llama el proyecto secreto y cuál es su presupuesto?",
                            "conversation_id": None}, timeout=60)
    assert chat.status_code == 200
    assert "Colibri" in chat.text or "48000" in chat.text or "48.000" in chat.text
