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

    # App
    app_env: str = "development"
    app_port: int = 8001

    # CORS — stored as comma-separated string, exposed as list
    allowed_origins: str = "http://localhost:4200"

    # PPT Profile Image Configuration
    ppt_profile_image_left: float = 1.0  # Horizontal position from left in inches
    ppt_profile_image_top: float = 0.1   # Vertical position from top in inches
    ppt_profile_image_width: float = 1.21  # Width in inches
    ppt_profile_image_height: float = 1.56  # Height in inches
    ppt_profile_image_rotation: int = 0  # Rotation in degrees
    ppt_profile_image_scale_width: float = 26.0  # Scale width percentage
    ppt_profile_image_scale_height: float = 26.0  # Scale height percentage

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()
