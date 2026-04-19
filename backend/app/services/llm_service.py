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
    "phone": "string",
    "location": "string"
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
      "startDate": "YYYY-MM or Month YYYY format",
      "endDate": "YYYY-MM or Month YYYY or Present format",
      "location": "work location/city",
      "projectName": "specific project name if mentioned",
      "projectInformation": "detailed project description and objectives",
      "clients": "client name/organization",
      "technology": ["tech1", "tech2", ...],
      "project_description": "overall project/role description",
      "achievements": ["responsibility1", "responsibility2", ...]
    }},
    ...
  ],
  "certifications": [
    {{
      "name": "certification name",
      "issuer": "issuing organization",
      "date": "date obtained"
    }},
    ...
  ]
}}

Extraction Rules:
- Extract full name from the top of the document
- Find email using regex patterns (look for patterns like name@domain.com)
- Find phone number using common formats
- Identify job title from professional titles mentioned
- Extract all work experience entries with DETAILED extraction:
  * employer: Company/Organization name (REQUIRED)
  * position: Job title/designation (REQUIRED)
  * startDate: CRITICAL - Look for dates in formats like "March 2023", "09/2023", "2023-03". Look for "Experience", "Work History" sections for dates.
  * endDate: CRITICAL - Look for end dates or "Present", "Current". Often appears after dash/hyphen after start date.
  * location: City/location - Look in parentheses after company, or in address sections
  * projectName: CRITICAL - Look for project names in CAPS, quoted text, or after "Project:" labels
  * projectInformation: CRITICAL - Look for project description paragraphs, objectives, and scope details
  * clients: CRITICAL - Look for "Client:" labels, client names in parentheses, or organization names
  * technology: CRITICAL - Look for tech stacks, comma-separated lists of tools/languages (Angular, React, Java, Python, AWS, etc.)
  * project_description: Comprehensive description of the work and responsibilities
  * achievements: List of key responsibilities, accomplishments, and contributions
- For work experience sections: Look for structured data with dates (Month YYYY – Month YYYY format), look for bullets with responsibilities, look for lines with company name and position
- Extract summary/objective section and split into logical sentences
- Parse skills section and categorize into primary (most important) and secondary
- Extract certifications with name, issuer, and date
- IMPORTANT: If dates appear on the same line as company/position (e.g., "Company Name (Jan 2023 – Present)"), extract them
- IMPORTANT: If project, client, or technology information is embedded in descriptions, extract and separate them
- If a specific field is not found, use empty string or empty array
- Be accurate and don't make up information

Return only valid JSON, no additional text.
"""

        messages = [
            {"role": "system", "content": "You are a CV parsing assistant. Always return valid JSON with all requested fields. Extract comprehensive details from work experience sections including company, dates, projects, clients, technologies, and responsibilities."},
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
