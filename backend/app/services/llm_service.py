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
  "education": [
    {{
      "institution": "university/college name",
      "degree": "B.E./B.Tech/M.S./etc",
      "field": "field of study/specialization",
      "startDate": "YYYY or YYYY-MM format",
      "endDate": "YYYY or YYYY-MM format"
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
- Extract education entries with DETAILED extraction: LOOK FOR THESE PATTERNS:
  * Look for degree types: B.E., B.Tech, M.S., M.Tech, MBA, B.Sc, B.A., BCom., M.A., B.Com, etc.
  * Look for institution names (usually capitalized, often followed by location/city/state)
  * Look for field/specialization patterns: "in [Field]", "[Field] Engineering", "[Field] Science", etc.
  * Fields include: "Electrical and Electronics Engineering", "Computer Science", "Business Administration", etc.
  * Look for CGPA/GPA (not required, just for reference)
  * Look for graduation years/dates like "2015", "2023", commonly on same line as degree or institution
  * EXAMPLE FORMAT FROM RESUMES: "R.M.D Engineering College, Chennai, TN. B.E. in Electrical and Electronics Engineering, 2015. CGPA: 7.9"
    - Extract: institution="R.M.D Engineering College, Chennai", degree="B.E.", field="Electrical and Electronics Engineering", endDate="2015"
  * Look for entries formatted like: "University Name, City. Degree in Field, Year." or "Degree in Field from University, Year"
  * Look in sections with headers: "Education", "Academic", "Qualifications", "Educational Background"
  * EVEN IF NO CLEAR HEADER: Look for bullets/lines with college names and degree patterns
  * CRITICAL: Extract ALL education entries found, even if just listed as bullets without an "Education" section header
  * Extract all of these components:
    - institution: College/University name (e.g., "R.M.D Engineering College, Chennai")
    - degree: Degree abbreviation (e.g., "B.E.", "B.Tech", "M.S.")
    - field: Field of study (e.g., "Electrical and Electronics Engineering")
    - endDate: Year of graduation (e.g., "2015", "2023")
- Extract certifications with name, issuer, and date
- IMPORTANT: If dates appear on the same line as company/position (e.g., "Company Name (Jan 2023 – Present)"), extract them
- IMPORTANT: If dates appear on the same line as degree/institution (e.g., "X.E. in Electronics Engineering, 2015" or "R.M.D Engineering College. B.E. in Electronics, 2015"), extract them
- IMPORTANT: If project, client, or technology information is embedded in descriptions, extract and separate them
- If a specific field is not found, use empty string or empty array
- Be accurate and don't make up information

Return only valid JSON, no additional text.
"""

        messages = [
            {"role": "system", "content": "You are a CV parsing assistant. Always return valid JSON with all requested fields. Extract comprehensive details from work experience and education sections including company, dates, projects, clients, technologies, responsibilities, institutions, degrees, and fields of study."},
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
