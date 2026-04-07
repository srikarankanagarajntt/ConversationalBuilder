import logging
import time
from typing import Any, Dict, List

from app.adapters.openai_adapter import OpenAIAdapter
from app.core.exceptions import LLMServiceError

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self._adapter = OpenAIAdapter()

    async def chat(
        self,
        messages: List[Dict[str, str]],
        response_format: str = "text",
    ) -> str:
        start_time = time.time()

        try:
            logger.info(
                "LLM chat request | messages=%d | response_format=%s",
                len(messages),
                response_format,
            )

            # optional: log first message preview (safe)
            if messages:
                logger.debug("First message preview: %s", messages[0]["content"][:200])

            result = await self._adapter.chat_completion(
                messages, response_format=response_format
            )

            duration = round(time.time() - start_time, 2)
            logger.info("LLM chat success | duration=%ss", duration)

            return result

        except Exception as exc:
            duration = round(time.time() - start_time, 2)

            logger.error(
                "LLM chat failed | duration=%ss | error=%s",
                duration,
                repr(exc),
                exc_info=True,  # 🔥 THIS prints full traceback
            )

            raise LLMServiceError(f"GPT call failed: {exc}") from exc