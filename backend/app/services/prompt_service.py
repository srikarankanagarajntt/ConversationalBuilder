"""Prompt engineering — builds all prompts sent to GPT-4.1."""
from __future__ import annotations

import json
from typing import Any, Dict, List


SYSTEM_PROMPT = """You are a professional CV builder assistant for NTT DATA employees.
Your role is to help users build a complete, high-quality CV through friendly conversation.
Always respond in clear, professional English.
When extracting or updating CV data, return valid JSON matching the CV schema.
When asking follow-up questions, ask only ONE question at a time."""

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
            "Instructions:\n"
            "1. Extract any new CV information from the user's message.\n"
            "2. Return a JSON object with two keys:\n"
            '   - "reply": your friendly reply text to show the user\n'
            '   - "cvUpdate": partial CV fields extracted from this message (may be empty {{}})\n'
            '   - "nextQuestion": the next question to ask (null if CV is complete)\n'
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
