import os
import httpx
import pytest

API = os.getenv("E2E_API_URL", "http://localhost:8000")
ERP = os.getenv("E2E_ERP_URL", "http://localhost:8080")

@pytest.mark.e2e
def test_login_then_facturas_pendientes():
    login = httpx.post(f"{ERP}/api/login", json={"email": "ana@idled.test"}, timeout=10)
    assert login.status_code == 200
    token = login.json()["token"]

    resp = httpx.get(
        f"{API}/api/erp/facturas-pendientes",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert resp.status_code == 200
    facturas = resp.json()
    assert all(f["pagada"] is False for f in facturas)
    assert any(f["id"] == "F-1001" for f in facturas)

@pytest.mark.e2e
def test_produccion_role_is_forbidden():
    token = httpx.post(f"{ERP}/api/login", json={"email": "pro@idled.test"}, timeout=10).json()["token"]
    resp = httpx.get(
        f"{API}/api/erp/facturas-pendientes",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert resp.status_code == 403
