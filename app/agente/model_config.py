from dataclasses import dataclass
from app.agente.openai_provider import OpenAIProvider
from app.agente.provider import LLMProvider
from app.core.config import get_settings

@dataclass(frozen=True)
class ModelProfile:
    provider: str
    model: str

def get_profile(name: str) -> ModelProfile:
    s = get_settings()
    profiles = {
        "chat": ModelProfile(s.model_chat_provider, s.model_chat),
        "search": ModelProfile(s.model_search_provider, s.model_search),
    }
    if name not in profiles:
        raise KeyError(f"Perfil de modelo desconocido: {name}")
    return profiles[name]

def build_provider_for(name: str) -> LLMProvider:
    profile = get_profile(name)
    if profile.provider == "openai":
        return OpenAIProvider(model=profile.model, api_key=get_settings().openai_api_key)
    raise ValueError(f"Proveedor LLM no soportado: {profile.provider}")
