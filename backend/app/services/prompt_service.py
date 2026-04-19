"""Prompt engineering — builds all prompts sent to GPT-4.1."""
from __future__ import annotations

import json
from typing import Any, Dict, List


SYSTEM_PROMPT = """You are a professional CV builder assistant for NTT DATA employees.
Your role is to help users build a complete, high-quality CV through friendly conversation.
Always respond in clear, professional English.

KEY RESPONSIBILITIES:
1. IDENTIFY MISSING INFORMATION: Always check the current CV draft for missing critical fields
2. ASK FOR MISSING DETAILS: If work experience is incomplete, ask for: start/end dates, project name, project description, client, and technologies
3. ELABORATE AND ENHANCE: Don't just accept user input as-is. Ask clarifying questions to understand their achievements better.
4. EXTRACT ACHIEVEMENTS: Convert job descriptions into quantifiable, impactful achievements.
5. SUGGEST IMPROVEMENTS: Offer suggestions to make their CV more compelling.
6. ASK ONE THING AT A TIME: Keep questions focused and easy to answer.
7. ACKNOWLEDGE RECEIPT: When user provides information, acknowledge that you've captured it before asking for more details

When extracting or updating CV data, return valid JSON matching the CV schema.
When you have information, enhance it with professional language and details.

CURRENT STRATEGY:
- First check what's already in the CV
- Ask for the most critical missing fields: project details, dates, client, technologies
- Be specific and reference what you've already captured
- Provide a friendly follow-up question focused on ONE missing field at a time
- Example: "Thank you for sharing your NTT Data experience. I've captured your role as System Integration Specialist. 
  Could you provide the project name you worked on and when you worked on it (start and end dates)? 
  Also, who was the client for this project?"""

CV_SCHEMA_DESCRIPTION = """
The CV schema has these fields:
- personalInfo: { fullName, email, phone, location, role, summary }
- skills: [string]
- experience: [{
    company, title, role, startDate, endDate, location,
    projectName, projectInformation, clients,
    technology: [string], description, achievements: [string]
  }]
- education: [{ institution, degree, field, startDate, endDate }]
- projects: [{ name, description, technologies: [string], url }]
- certifications: [{ name, issuer, date }]
- languages: [string]
"""


class PromptService:
    def build_conversation_prompt(
        self,
        conversation_history: List[Dict[str, str]],
        cv_draft_json: str,
        user_message: str,
    ) -> List[Dict[str, str]]:
        """Build the full message list for a conversational CV building turn."""
        system_content = (
            f"{SYSTEM_PROMPT}\n\n"
            f"{CV_SCHEMA_DESCRIPTION}\n\n"
            "Current CV draft (JSON):\n"
            f"{cv_draft_json}\n\n"
            "Instructions for this conversation turn:\n"
            "1. FIRST: Review the CV draft above and identify ANY MISSING CRITICAL FIELDS in work experience entries:\n"
            "   - startDate, endDate (employment duration) - CRITICAL\n"
            "   - projectName (specific project worked on) - CRITICAL\n"
            "   - projectInformation (what the project does, objectives) - CRITICAL\n"
            "   - clients (client organization/company) - CRITICAL\n"
            "   - technology (technologies, tools, languages used) - CRITICAL\n"
            "2. If critical fields are empty: Your PRIMARY task is to ask for those missing details\n"
            "3. ACKNOWLEDGE what you've received: Start with 'Thank you for sharing... I've captured [what they told you]...'\n"
            "4. Then ask ONE missing field at a time - be specific about which field you need\n"
            "5. If they provide new info:\n"
            "   - Extract and structure it\n"
            "   - Enhance with professional language\n"
            "   - List what you need next\n"
            "6. Priority order for asking missing details:\n"
            "   a. Work experience dates (startDate, endDate)\n"
            "   b. Project name and information\n"
            "   c. Client name\n"
            "   d. Technologies used\n"
            "   e. Specific achievements/metrics\n"
            "7. Return a JSON object with:\n"
            '   - "reply": your friendly message acknowledging what you captured + asking for the next missing field\n'
            '   - "cvUpdate": extracted CV fields from this message (or empty {} if only asking for info)\n'
            '   - "nextQuestion": specific follow-up question for the next critical missing field\n'
        )
        messages: List[Dict[str, str]] = [{"role": "system", "content": system_content}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        return messages

    def build_extraction_prompt(self, raw_text: str) -> List[Dict[str, str]]:
        """Build the prompt for extracting structured CV data from raw text."""
        system_content = (
            f"{SYSTEM_PROMPT}\n\n"
            f"{CV_SCHEMA_DESCRIPTION}\n\n"
            "Extract all CV information from the following text and return a JSON object "
            "matching the CV schema exactly.  Use empty strings or empty arrays for missing fields."
        )
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": f"Extract CV data from:\n\n{raw_text}"},
        ]

    def build_follow_up_prompt(
        self, cv_json: str, missing_fields: List[str]
    ) -> List[Dict[str, str]]:
        """Build a prompt that generates the next follow-up question."""
        system_content = (
            f"{SYSTEM_PROMPT}\n\n"
            "Given the current CV draft and the list of missing fields, "
            "generate ONE friendly, specific question to collect the most important missing information."
        )
        user_content = (
            f"Current CV (JSON):\n{cv_json}\n\n"
            f"Missing fields: {', '.join(missing_fields)}\n\n"
            "What is your next question?"
        )
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]
    def build_elaboration_prompt(
        self, cv_json: str, field_type: str = "experience"
    ) -> List[Dict[str, str]]:
        """Build a prompt to ask for elaboration on a specific field."""
        elaboration_prompts = {
            "experience": "Tell me more about one of your work experiences. What were key achievements? Any metrics or results? What technologies did you use?",
            "education": "Tell me about your education. What degree did you earn? What field of study? Any relevant coursework or honors?",
            "projects": "Describe a project you've worked on. What was it? What was your role? What was the outcome?",
            "skills": "What are your top technical or professional skills? Any certifications or specializations?"
        }
        system_content = (
            f"{SYSTEM_PROMPT}\n\n"
            "Your task is to ask a question that encourages the user to provide more detailed information "
            "about their CV. Make it specific and easy to answer."
        )
        user_content = elaboration_prompts.get(
            field_type,
            "Tell me more about yourself so I can make your CV more compelling."
        )
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]