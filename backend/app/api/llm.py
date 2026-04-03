"""POC LLM endpoint for quick GPT-4.1 integration validation."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.llm_service import LLMService

router = APIRouter()
llm_service = LLMService()


class LLMTestRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)


class LLMTestResponse(BaseModel):
    model: str
    output: str


@router.post("/llm/test", response_model=LLMTestResponse)
async def llm_test(
    body: LLMTestRequest,
):
    """Run a simple GPT call to validate API key + model wiring."""
    messages = [
        {
            "role": "system",
            "content": "You are a concise assistant helping with CV building.",
        },
        {
            "role": "user",
            "content": body.prompt,
        },
    ]
    output = await llm_service.chat(messages)
    return LLMTestResponse(model=settings.openai_model, output=output)
