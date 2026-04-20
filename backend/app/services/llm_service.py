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
IMPORTANT: When extracting professional summaries and achievements, always ELABORATE AND ENHANCE minimal details with relevant insights.

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
  "professionalSummary": [
    "comprehensive summary sentence 1",
    "expertise areas and specializations",
    "methodologies and best practices",
    "key achievements or focus areas",
    "career objectives and value proposition"
  ],
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
      "project_description": "comprehensive role and project description",
      "achievements": [
        "key accomplishment 1 with context and impact",
        "key accomplishment 2 with metrics or business value",
        "challenge overcome with approach taken",
        "technical excellence or innovation contributed",
        "collaboration or leadership example"
      ]
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

CRITICAL INSTRUCTION - ELABORATION FOR MINIMAL DETAILS:
- If professional summary is 1 sentence or very brief: Expand it to 4-5 comprehensive sentences by:
  * Adding specific expertise areas and technologies
  * Mentioning methodologies and best practices they follow
  * Including years of experience and industry focus
  * Describing their unique value proposition and approach
  * Highlighting specializations within their role
  EXAMPLE: If given "Full Stack Developer with 10 years Java and Angular"
  EXPAND TO: [
    "Full Stack Developer with 10+ years of specialized experience in enterprise Java backend development and modern Angular frontend frameworks.",
    "Expert in designing and implementing microservices architectures, REST APIs, and scalable system design using Spring Boot, Quarkus, and modern cloud patterns.",
    "Proficient in full-stack development combining backend expertise (Java, Spring, Hibernate, SQL) with frontend excellence (Angular, TypeScript, RxJS, responsive design).",
    "Demonstrated ability to lead technical initiatives across entire development lifecycle while mentoring junior developers and establishing best practices in code quality and testing.",
    "Strong focus on performance optimization, security hardening, and DevOps integration to deliver robust, production-ready applications."
  ]

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
  * achievements: CRITICAL - Extract and ELABORATE on achievements:
    - Look for bullet points, responsibilities, or accomplishment statements
    - For EACH achievement found or inferred:
      * Add context about the task/project/challenge
      * Include business impact, metrics, or results (e.g., "improved performance by 40%", "served 500+ users")
      * Mention technologies or methodologies used
      * Reference scale/scope (team size, project size, user base, etc.)
      * If vague, infer reasonable details from role/company context
    - Generate 5-7 elaborated achievement statements per work experience entry
    - Format: "[ACTION] [TASK] [TECHNOLOGY/APPROACH] [IMPACT/RESULT] [SCOPE/CONTEXT]"
    - Examples:
      "Architected microservices infrastructure using Spring Boot and Docker, reducing deployment time by 60% and enabling 10x faster release cycles"
      "Implemented Angular-based responsive UI serving 500K+ daily active users across web and mobile platforms with sub-100ms load times"
      "Led technical initiative to migrate legacy monolith to cloud-native architecture, resulting in $2M annual infrastructure cost reduction"
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
