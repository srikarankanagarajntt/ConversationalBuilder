import json
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

    async def extract_cv_data(self, raw_text: str) -> Dict[str, Any]:
        """
        Use LLM to extract structured CV data from raw text.
        Returns data in the format expected by CvSchema.
        """
        prompt = f"""
You are an expert CV parser. Extract structured information from the following CV text and return it as JSON.

CV Text:
{raw_text}

Please extract the following information and format it as JSON with these exact keys:

{{
  "header": {{
    "fullName": "string",
    "jobTitle": "string", 
    "email": "string",
    "phone": "string"
  }},
  "professionalSummary": ["sentence1", "sentence2", ...],
  "technicalSkills": {{
    "primary": [
      {{"skill_name": "skill1", "proficiency": "expert|advanced|intermediate|beginner"}},
      ...
    ],
    "secondary": [
      {{"skill_name": "skill2", "proficiency": "expert|advanced|intermediate|beginner"}},
      ...
    ]
  }},
  "workExperience": [
    {{
      "employer": "company name",
      "position": "job title",
      "project_description": "description of work"
    }},
    ...
  ]
}}

Rules:
- Extract full name from the top of the document
- Find email using regex patterns
- Find phone number using common formats
- Identify job title from professional titles mentioned
- Extract summary/objective section and split into logical sentences
- Parse skills section and categorize into primary (most important) and secondary
- Extract work experience entries with employer, position, and descriptions
- If information is not found, use empty strings or empty arrays
- Be accurate and don't make up information

Return only valid JSON, no additional text.
"""

        messages = [
            {"role": "system", "content": "You are a CV parsing assistant. Always return valid JSON."},
            {"role": "user", "content": prompt}
        ]

        try:
            response = await self.chat(messages, response_format="json_object")
            # Parse the JSON response
            extracted_data = json.loads(response)
            return extracted_data
        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM response as JSON: %s", e)
            raise LLMServiceError(f"Invalid JSON response from LLM: {e}") from e
        except Exception as e:
            logger.error("LLM extraction failed: %s", str(e))
            raise
