from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

class ExportAsset(BaseModel):
    kind: Literal["docx", "pptx"]
    file_name: str
    base64: str | None = None

class ExportManifest(BaseModel):
    session_id: str
    template_id: str
    assets: list[ExportAsset] = Field(default_factory=list)
    available_outputs: list[Literal["pdf", "docx", "pptx", "json"]] = Field(default_factory=lambda: ["pdf", "json"])
