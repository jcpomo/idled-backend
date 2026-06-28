import jwt as pyjwt
import pytest
from app.auth.jwt import decode_token, InvalidTokenError
from app.auth.roles import Role

SECRET = "test-secret"

def _make(payload, secret=SECRET):
    return pyjwt.encode(payload, secret, algorithm="HS256")

def test_decode_valid_token(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", SECRET)
    from app.core.config import get_settings
    get_settings.cache_clear()
    token = _make({"sub": "u-1", "role": "administracion", "name": "Ana"})
    payload = decode_token(token)
    assert payload.user_id == "u-1"
    assert payload.role == Role.ADMINISTRACION
    assert payload.name == "Ana"

def test_decode_bad_signature(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", SECRET)
    from app.core.config import get_settings
    get_settings.cache_clear()
    token = _make({"sub": "u-1", "role": "administracion"}, secret="wrong")
    with pytest.raises(InvalidTokenError):
        decode_token(token)

def test_decode_invalid_role_raises(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", SECRET)
    from app.core.config import get_settings
    get_settings.cache_clear()
    token = _make({"sub": "u-1", "role": "not_a_real_role", "name": "X"})
    with pytest.raises(InvalidTokenError):
        decode_token(token)
