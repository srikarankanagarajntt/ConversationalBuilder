import json
import logging
import re
import time

import httpx
from openai import AsyncOpenAI

import os
import certifi


certifi.where()



os.environ["REQUESTS_CA_BUNDLE"] = "C:/Users/345131/Documents/CONFIDENTIAL/Hackathon/Conversational_Image_Builder/codebase/ConversationalBuilder/certs/openai.crt"

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class OpenAIAdapter:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.openai_model
        self.api_key = settings.openai_api_key
        verify: bool | str = settings.openai_ssl_verify
        if settings.openai_ca_bundle_path:
            verify = settings.openai_ca_bundle_path
        self.http_client = httpx.AsyncClient(verify=verify)
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            timeout=settings.openai_timeout_seconds,
            max_retries=settings.openai_max_retries,
            http_client=self.http_client,
        )

    @staticmethod
    def _extract_latest_user_message(prompt: str) -> str:
        marker = "Latest user message:\n"
        if marker not in prompt:
            return prompt
        return prompt.split(marker, 1)[1].strip()

    @staticmethod
    def _heuristic_updates(message: str) -> dict:
        text = " ".join(message.split())
        updates: dict = {}

        name_match = re.search(r"\bmy name is\s+([a-zA-Z][a-zA-Z\s]{1,80})", text, flags=re.IGNORECASE)
        if name_match:
            full_name = re.sub(r"\s+", " ", name_match.group(1)).strip(" .,-")
            if full_name:
                updates.setdefault("header", {})["fullName"] = full_name.title()

        role_match = re.search(
            r"\b(?:i am|i'm|am)\s+([a-zA-Z][a-zA-Z\s]{1,80}?)(?:\s+(?:with|having|has)\b|[,.]|$)",
            text,
            flags=re.IGNORECASE,
        )
        if role_match:
            role = re.sub(r"\s+", " ", role_match.group(1)).strip(" .,-")
            if role:
                updates.setdefault("header", {})["jobTitle"] = role.title()

        return updates

    async def generate_structured_response(self, prompt: str) -> dict:
        user_message = self._extract_latest_user_message(prompt)
        heuristic_updates = self._heuristic_updates(user_message)

        fallback = {
            "assistant_message": "Thanks. Please share your current responsibilities and primary technical skills.",
            "updates": heuristic_updates,
        }

        if not self.api_key or self.api_key == "change-me":
            logger.warning("OpenAI API key missing or placeholder value set. Returning fallback response.")
            return fallback

        system_prompt = (
            "You are a CV assistant. Return ONLY valid JSON with this exact shape: "
            "{\"assistant_message\": string, \"updates\": object}. "
            "The updates object can include partial fields like header.fullName, header.jobTitle, "
            "professionalSummary, technicalSkills, currentResponsibilities, workExperience, personalDetails, declaration. "
            "Ask one concise next question in assistant_message."
        )

        start_time = time.perf_counter()
        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            logger.info(
                "OpenAI chat completion completed in %d ms (model=%s, prompt_chars=%d)",
                elapsed_ms,
                self.model,
                len(prompt),
            )
            raw = (completion.choices[0].message.content or "").strip()
            parsed = json.loads(raw) if raw else {}
            assistant_message = parsed.get("assistant_message")
            updates = parsed.get("updates")

            if isinstance(assistant_message, str) and isinstance(updates, dict):
                return {"assistant_message": assistant_message, "updates": updates}
            logger.warning("OpenAI response did not match expected JSON schema. Returning fallback response.")
            return fallback
        except Exception as exc:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            logger.exception(
                "OpenAI call failed after %d ms (model=%s, prompt_chars=%d); returning fallback response: %s",
                elapsed_ms,
                self.model,
                len(prompt),
                exc,
            )
            return fallback

_openai_adapter = OpenAIAdapter()

def get_openai_adapter() -> OpenAIAdapter:
    return _openai_adapter
