import pytest
from app.agente.model_config import ModelProfile, get_profile, build_provider_for
from app.agente.openai_provider import OpenAIProvider

def _clear():
    from app.core.config import get_settings
    get_settings.cache_clear()

def test_get_profile_defaults(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    _clear()
    assert get_profile("chat") == ModelProfile(provider="openai", model="gpt-4o")
    assert get_profile("search") == ModelProfile(provider="openai", model="gpt-4o-mini")

def test_profile_overridable_by_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("MODEL_CHAT", "gpt-4o-2026")
    _clear()
    assert get_profile("chat").model == "gpt-4o-2026"

def test_build_provider_for_chat(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    _clear()
    prov = build_provider_for("chat")
    assert isinstance(prov, OpenAIProvider)
    assert prov._model == "gpt-4o"

def test_unknown_profile_raises(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    _clear()
    with pytest.raises(KeyError):
        get_profile("nope")

def test_unknown_provider_raises(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("MODEL_CHAT_PROVIDER", "acme")
    _clear()
    with pytest.raises(ValueError):
        build_provider_for("chat")
