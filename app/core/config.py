from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    erp_base_url: str
    qdrant_url: str = "http://qdrant:6333"
    redis_url: str = "redis://redis:6379"

    model_chat_provider: str = "openai"
    model_chat: str = "gpt-4o"
    model_search_provider: str = "openai"
    model_search: str = "gpt-4o-mini"
    openai_api_key: str = ""

@lru_cache
def get_settings() -> Settings:
    return Settings()
