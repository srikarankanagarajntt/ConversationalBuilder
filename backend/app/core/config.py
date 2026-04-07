"""Application settings loaded from environment / .env file."""
from __future__ import annotations

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict  # noqa: F401


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1"
    openai_max_tokens: int = 2048
    openai_temperature: float = 0.3

    # Whisper
    whisper_model: str = "whisper-1"

    # Text-to-speech
    tts_model: str = "gpt-4o-mini-tts"
    tts_voice: str = "alloy"
    tts_format: str = "mp3"

    # App
    app_env: str = "development"
    app_port: int = 8000

    # CORS — stored as comma-separated string, exposed as list
    allowed_origins: str = "http://localhost:4200"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()
