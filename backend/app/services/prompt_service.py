"""Prompt engineering — builds all prompts sent to GPT-4.1."""
from __future__ import annotations

import json
from typing import Any, Dict, List


SYSTEM_PROMPT = """You are a professional CV builder assistant for NTT DATA employees.
Your role is to help users build a complete, high-quality CV through friendly conversation.
Always respond in clear, professional English.

KEY RESPONSIBILITIES:
1. ELABORATE AND ENHANCE: Don't just accept user input as-is. Ask clarifying questions to understand their achievements better.
2. EXTRACT ACHIEVEMENTS: Convert job descriptions into quantifiable, impactful achievements.
3. SUGGEST IMPROVEMENTS: Offer suggestions to make their CV more compelling.
4. ASK Multiple THING AT A TIME: Keep questions focused and easy to answer.

When extracting or updating CV data, return valid JSON matching the CV schema.
When you have information, enhance it with professional language and details."""

CV_SCHEMA_DESCRIPTION = """
The CV schema has these fields:
- personalInfo: { fullName, email, phone, location, linkedin, summary }
- skills: [string]
- experience: [{ company, title, startDate, endDate, achievements: [string] }]
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
            "1. Analyze the user's message carefully.\n"
            "2. If they provide experience/project info without details:\n"
            "   - Extract what they said\n"
            "   - Enhance it with professional language\n"
            "   - Ask a follow-up question to get more details (achievements, metrics, technologies, etc.)\n"
            "3. If they provide basic info, suggest questions to elaborate (What was the impact? Any metrics? What technologies?)\n"
            "4. Return a JSON object with:\n"
            '   - "reply": your friendly message with extraction acknowledgment + follow-up question\n'
            '   - "cvUpdate": enhanced/extracted CV fields from this message (may be empty {{}})\n'
            '   - "nextQuestion": the next follow-up question (null if waiting for them to provide more details)\n'
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