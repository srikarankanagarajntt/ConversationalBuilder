from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Conversational CV Builder API"
    app_version: str = "0.2.0"
    environment: str = "dev"
    allowed_origins: list[str] = ["*"]

    openai_api_key: str = "change-me"
    openai_model: str = "gpt-4.1"
    openai_audio_model: str = "whisper-1"

    okta_issuer: str = "https://example.okta.com/oauth2/default"
    okta_audience: str = "api://default"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
