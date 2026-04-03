"""Run a direct GPT-4.1 integration smoke test.

Usage:
    python tests/test_llm_integration.py
"""
from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv

from app.services.llm_service import LLMService


async def main() -> None:
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is missing. Set it in backend/.env before running this script.")

    service = LLMService()
    response = await service.chat(
        [
            {
                "role": "system",
                "content": "You are a concise CV assistant.",
            },
            {
                "role": "user",
                "content": "Write two resume bullets for a Python FastAPI developer with Angular experience.",
            },
        ]
    )

    print("LLM integration success. Model reply:\n")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
