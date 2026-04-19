"""Conversation orchestration service."""
from __future__ import annotations

import json
from typing import Any, Dict

from app.models.responses import ConversationResponse
from app.services.state_service import StateService
from app.services.llm_service import LLMService
from app.services.prompt_service import PromptService
from app.services.cv_schema_service import CvSchemaService
from app.services.validation_service import ValidationService


class ConversationService:
    def __init__(self, state_service: StateService):
        self._state = state_service
        self._llm = LLMService()
        self._prompts = PromptService()
        self._cv_schema = CvSchemaService()
        self._validation = ValidationService()

    async def handle_message(self, session_id: str, user_message: str) -> ConversationResponse:
        """
        Core conversation loop:
        1. Load session state
        2. Check if this is initial message → trigger personal info modal
        3. Build prompt with current CV draft + history
        4. Call GPT-4.1 with elaboration focus
        5. Parse AI response → extract CV updates
        6. Merge into draft, validate, persist
        7. Return reply + updated draft
        """
        session = self._state.get_session(session_id)

        # Check BEFORE adding message if this should trigger personal info modal
        # This is the first user message if conversationHistory is still empty (greeting is only on frontend)
        should_show_modal = (
            not session.cvDraft.personalInfo.fullName and 
            len(session.conversationHistory) == 0  # No messages on backend yet
        )

        # Persist user message
        self._state.add_message(session_id, "user", user_message)

        # If we should show modal, return early with modal flag
        if should_show_modal:
            reply_text = f"Great! Let me gather your information first to build a better CV for you."
            self._state.add_message(session_id, "assistant", reply_text)
            return ConversationResponse(
                sessionId=session_id,
                reply=reply_text,
                cvDraft=session.cvDraft,
                missingFields=self._validation.get_missing_fields(session.cvDraft),
                nextQuestion=None,
                showPersonalInfoModal=True,
            )

        # Build history for the LLM (max last 20 turns to keep tokens manageable)
        history = [
            {"role": m.role, "content": m.content}
            for m in session.conversationHistory[-20:]
        ]

        cv_json = session.cvDraft.model_dump_json(indent=2)
        messages = self._prompts.build_conversation_prompt(history, cv_json, user_message)

        raw_response = await self._llm.chat(messages, response_format="json_object")

        # Parse structured response from GPT
        parsed: Dict[str, Any] = {}
        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError:
            # Graceful fallback — treat entire response as plain reply
            parsed = {"reply": raw_response, "cvUpdate": {}, "nextQuestion": None}

        reply_text = parsed.get("reply", "I could not understand that. Please try again.")
        cv_update = parsed.get("cvUpdate", {})
        next_question = parsed.get("nextQuestion")

        # Merge AI-extracted fields into the draft
        if cv_update:
            updated_cv = self._cv_schema.merge_partial_update(session.cvDraft, cv_update)
            self._state.update_cv(session_id, updated_cv)
        else:
            updated_cv = session.cvDraft

        # Validate and compute missing fields
        missing = self._validation.get_missing_fields(updated_cv)
        self._state.update_missing_fields(session_id, missing)

        # Persist assistant reply
        self._state.add_message(session_id, "assistant", reply_text)

        return ConversationResponse(
            sessionId=session_id,
            reply=reply_text,
            cvDraft=updated_cv,
            missingFields=missing,
            nextQuestion=next_question,
            showPersonalInfoModal=False,
        )

    async def handle_personal_info_submission(
        self,
        session_id: str,
        full_name: str,
        email: str,
        phone: str,
        location: str,
        summary: str,
        skills: list,
    ) -> ConversationResponse:
        """
        Handle personal info modal submission.
        1. Update CV with personal info + skills
        2. Populate professionalSummary and technicalSkills for preview
        3. Generate encouraging message
        4. Ask first follow-up question about experience
        """
        import re
        session = self._state.get_session(session_id)

        # Split summary into sentences for professionalSummary
        professional_summary = []
        if summary:
            # Clean the summary: remove extra newlines and spaces
            cleaned_summary = ' '.join(summary.split())
            # Split by sentence delimiters
            sentences = re.split(r'[.!?]+', cleaned_summary)
            # Strip whitespace and filter out empty strings
            professional_summary = [s.strip() for s in sentences if s.strip()]
            # Ensure we have at least something
            if not professional_summary:
                professional_summary = [cleaned_summary]

        # Categorize skills into primary and secondary
        technical_skills = {"primary": [], "secondary": []}
        if skills:
            # First half as primary, second half as secondary
            midpoint = len(skills) // 2 + 1
            for i, skill in enumerate(skills):
                if i < midpoint:
                    technical_skills["primary"].append({
                        "skillName": skill,
                        "proficiency": "advanced"
                    })
                else:
                    technical_skills["secondary"].append({
                        "skillName": skill,
                        "proficiency": "intermediate"
                    })

        # Build personal info update
        cv_update = {
            "personalInfo": {
                "fullName": full_name,
                "email": email,
                "phone": phone,
                "location": location,
                "summary": summary,
            },
            "skills": skills,
            "professionalSummary": professional_summary,
            "technicalSkills": technical_skills,
            "header": {
                "fullName": full_name,
                "email": email,
                "phone": phone,
                "jobTitle": ""
            }
        }

        # Update CV with personal info
        updated_cv = self._cv_schema.merge_partial_update(session.cvDraft, cv_update)
        
        # Ensure professional summary and technical skills are properly set (direct assignment to override any conflicts)
        updated_cv.professionalSummary = professional_summary
        updated_cv.technicalSkills = technical_skills
        
        self._state.update_cv(session_id, updated_cv)

        # Generate AI-enhanced summary if basic one provided
        if summary:
            enhanced_summary = await self._llm.chat(
                [
                    {
                        "role": "system",
                        "content": "You are a professional CV writer. Given a summary, enhance it to be more impactful and professional. Keep it to 3-4 sentences.",
                    },
                    {"role": "user", "content": f"Enhance this summary:\n{summary}"},
                ],
                response_format="text",
            )
            updated_cv.personalInfo.summary = enhanced_summary.strip()
            
            # Re-split the enhanced summary into sentences for professionalSummary
            cleaned_enhanced = ' '.join(enhanced_summary.strip().split())
            enhanced_sentences = re.split(r'[.!?]+', cleaned_enhanced)
            enhanced_professional_summary = [s.strip() for s in enhanced_sentences if s.strip()]
            # Ensure we have at least something
            if not enhanced_professional_summary:
                enhanced_professional_summary = [cleaned_enhanced]
            updated_cv.professionalSummary = enhanced_professional_summary
            
            self._state.update_cv(session_id, updated_cv)

        # Determine next question based on what's missing
        missing = self._validation.get_missing_fields(updated_cv)
        self._state.update_missing_fields(session_id, missing)

        # Generate next question (focus on experience first)
        next_question = "Great! Now tell me about your professional experience. What's your current or most recent role?"

        # Add system messages
        self._state.add_message(
            session_id,
            "assistant",
            f"Perfect! I've saved your information, {full_name}. {next_question}",
        )

        return ConversationResponse(
            sessionId=session_id,
            reply=f"Perfect! I've saved your information, {full_name}. {next_question}",
            cvDraft=updated_cv,
            missingFields=missing,
            nextQuestion=next_question,
            showPersonalInfoModal=False,
        )