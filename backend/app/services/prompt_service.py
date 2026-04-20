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
4. EXTRACT ACHIEVEMENTS: Convert job descriptions into quantifiable, impactful achievements with metrics and business impact.
5. SUGGEST IMPROVEMENTS: Offer suggestions to make their CV more compelling with specific, measurable accomplishments.
6. ASK ONE THING AT A TIME: Keep questions focused and easy to answer.
7. ACKNOWLEDGE RECEIPT: When user provides information, acknowledge that you've captured it before asking for more details
8. ENHANCE MINIMAL DETAILS: When users provide minimal information:
   - For professional summaries: Add expertise areas, methodologies, specializations, and unique value proposition
   - For achievements: Add context, business impact, metrics, technologies used, and scope/scale
   - For roles & responsibilities: Ask for specific examples and quantifiable results
   - Ask follow-up questions like: "What was the business impact?", "What metrics improved?", "How many users/clients?", "What technologies?"
9. PROFESSIONAL SUMMARY ENHANCEMENT: If they provide a one-line professional summary, ask for elaboration on:
   - Specific technical expertise and technology stacks
   - Years of experience in specific domains/areas
   - Key specializations and methodologies they follow
   - Notable achievements or certifications
   - Career focus and unique value proposition

IMPORTANT - INTELLIGENT TECHNICAL SKILLS CATEGORIZATION FOR ANY PROFESSIONAL:
This system automatically and intelligently categorizes technical skills into Primary (7) and Secondary (7) for ANY professional role:

FOR PREDEFINED ROLES (auto-detected from summary + skills):
- Java/Backend Developers: Java, Spring, REST APIs → PRIMARY; Docker, CI/CD, Testing → SECONDARY
- Angular/Frontend Developers: Angular, TypeScript, HTML/CSS → PRIMARY; NgRx, Testing, Performance → SECONDARY
- Full-Stack Developers: Java, Angular, REST APIs → PRIMARY; Docker, CI/CD, Cloud → SECONDARY

FOR ANY OTHER PROFESSIONAL ROLE (ETL, Data Engineer, DevOps, Data Science, etc.):
The system uses INTELLIGENT LLM-BASED MAPPING to:
1. Detect the professional's role/specialization from their summary
2. Analyze provided skills to determine expertise areas
3. Generate 7 PRIMARY skills: Core technical competencies essential for their role
4. Generate 7 SECONDARY skills: Important complementary skills that enhance their profile

Examples of intelligent mapping:
- ETL Developer (Teradata, Oracle, Databricks) → PRIMARY: ETL Tools, Data Warehousing, SQL, Data Integration → SECONDARY: Cloud Platforms, Python, Data Modeling
- Data Scientist (Python, ML, Spark) → PRIMARY: Machine Learning, Python, Data Analysis → SECONDARY: Cloud Platforms, Big Data Tools, Statistical Methods
- DevOps Engineer (Docker, Kubernetes, CI/CD) → PRIMARY: Container Orchestration, CI/CD Pipelines, Infrastructure as Code → SECONDARY: Cloud Platforms, Monitoring, Automation

KEY SYSTEM BEHAVIOR:
- You DO NOT need to manually categorize skills - the system handles this automatically
- The system detects role from professional summary AND provided skills to ensure accuracy
- All roles (Java, Angular, Full-Stack, ETL, Data, DevOps, etc.) are supported
- Proficiency levels are intelligently assigned based on role and experience
- When discussing skills, refer to the user's technical expertise and confirm they match their role

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
            "1. FIRST: Review the CV draft above and check if professional summary is minimal (1-2 sentences) or achievements lack detail:\n"
            "   - If personalInfo.summary is 1-2 short sentences: Ask for elaboration on expertise, specializations, career focus\n"
            "   - If any work experience has generic/vague achievements: Ask for specific accomplishments with metrics\n"
            "2. SECOND: Review the CV draft above and identify ANY MISSING CRITICAL FIELDS in work experience entries:\n"
            "   - startDate, endDate (employment duration) - CRITICAL\n"
            "   - projectName (specific project worked on) - CRITICAL\n"
            "   - projectInformation (what the project does, objectives) - CRITICAL\n"
            "   - clients (client organization/company) - CRITICAL\n"
            "   - technology (technologies, tools, languages used) - CRITICAL\n"
            "   - achievements (specific accomplishments with metrics/impact) - CRITICAL\n"
            "3. If critical fields are empty: Your PRIMARY task is to ask for those missing details\n"
            "4. ACKNOWLEDGE what you've received: Start with 'Thank you for sharing... I've captured [what they told you]...'\n"
            "5. Then ask ONE missing field at a time - be specific about which field you need\n"
            "6. If they provide new info:\n"
            "   - Extract and structure it\n"
            "   - Enhance with professional language and ask for details if vague\n"
            "   - List what you need next\n"
            "7. IMPORTANT - ONLY UPDATE EXTRACTED FIELDS:\n"
            "   - Only include fields in cvUpdate that the user provided or you extracted from their message\n"
            "   - DO NOT clear or empty out existing fields that are already populated\n"
            "   - Example: If user says 'I worked in Bangalore', only extract location. Don't extract empty title, role, dates, etc.\n"
            "   - The backend will automatically merge your extracted fields with existing data\n"
            "8. Priority order for asking missing details:\n"
            "   a. Professional summary elaboration (if minimal) - ask about expertise, specializations, technologies, years of experience\n"
            "   b. Work experience dates (startDate, endDate)\n"
            "   b. Work experience dates (startDate, endDate)\n"
            "   c. Project name and information\n"
            "   d. Client name\n"
            "   e. Technologies used\n"
            "   f. Specific achievements/metrics with business impact\n"
            "9. When asking about achievements, guide them with examples:\n"
            "   - \"What specific accomplishments did you achieve in this role?\"\n"
            "   - \"Were there any metrics you improved (performance, users, cost)?\"\n"
            "   - \"How many users/clients/team members were impacted by your work?\"\n"
            "   - \"What technologies did you use and any innovation you introduced?\"\n"
            "10. When professional summary is brief, elaborate by asking:\n"
            "   - \"What are your core technical expertise areas?\"\n"
            "   - \"What methodologies or architectural approaches do you specialize in?\"\n"
            "   - \"What's your unique value proposition or career focus?\"\n"
            "   - \"Any certifications, specializations, or notable achievements?\"\n"
            "8. Return a JSON object with:\n"
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
            "matching the CV schema exactly. Use empty strings or empty arrays for missing fields.\n\n"
            "IMPORTANT - PROFESSIONALSUMMARY AND ACHIEVEMENTS ELABORATION:\n"
            "- If the professional summary is minimal (1-2 sentences), elaborate it into 4-5 comprehensive sentences that include:\n"
            "  * Specific technologies, frameworks, and tools they specialize in\n"
            "  * Years of experience and domain expertise\n"
            "  * Key methodologies, architectural approaches, and best practices they follow\n"
            "  * Unique value proposition and career focus\n"
            "  * Leadership, mentoring, or innovation contributions\n"
            "- If achievements are generic or vague, enhance them with:\n"
            "  * Specific business impact and measurable results\n"
            "  * Technologies and methodologies employed\n"
            "  * Scale and scope (team size, user base, performance metrics)\n"
            "  * Context about challenges overcome and solutions provided\n"
            "  * Format: [ACTION VERB] [SPECIFIC TASK] [USING TECHNOLOGY/APPROACH] [RESULTING IN IMPACT/METRIC] [AT SCALE/SCOPE]"
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
            "skills": "What are your top technical or professional skills? Any certifications or specializations?",
            "professional_summary": "Could you tell me more about your professional background? What are your core technical expertise areas, key specializations, methodologies you follow, and your unique value proposition in your field?"
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

    def _is_professional_summary_minimal(self, summary: str) -> bool:
        """Check if professional summary is minimal (too brief)."""
        if not summary:
            return True
        # If summary is less than 150 characters or just 1-2 sentences, consider it minimal
        sentence_count = len([s.strip() for s in summary.split('.') if s.strip()])
        return len(summary) < 150 or sentence_count < 2

    def _are_achievements_minimal(self, achievements: List[str]) -> bool:
        """Check if achievements are minimal or generic."""
        if not achievements:
            return True
        # Check if achievements are generic or lack detail (short length or generic verbs)
        generic_phrases = ['worked on', 'responsible for', 'involved in', 'participated in', 'helped with']
        for achievement in achievements:
            if len(achievement) < 50:  # Too short
                return True
            achievement_lower = achievement.lower()
            if any(phrase in achievement_lower for phrase in generic_phrases):
                if not any(word in achievement_lower for word in ['improved', 'increased', 'reduced', 'achieved', 'implemented', '%', 'times', 'users', 'customers']):
                    return True
        return False

    def build_minimal_details_prompt(self, cv_json: str) -> tuple:
        """
        Analyze CV and identify areas needing elaboration.
        Returns (question, field_type) tuple for the most important elaboration needed.
        """
        import json as json_lib
        
        try:
            cv_data = json_lib.loads(cv_json) if isinstance(cv_json, str) else cv_json
        except:
            return None, None

        # Check professional summary first (highest priority)
        personal_info = cv_data.get('personalInfo', {})
        if personal_info:
            summary = personal_info.get('summary', '')
            if self._is_professional_summary_minimal(summary):
                return (
                    "I noticed your professional summary is quite brief. Could you help me elaborate on it? "
                    "What are your core technical expertise areas and specializations? What methodologies or architectural approaches do you specialize in? "
                    "What makes you unique in your field?",
                    'professional_summary'
                )

        # Check work experience achievements
        experience = cv_data.get('experience', [])
        for exp in experience:
            achievements = exp.get('achievements', [])
            if self._are_achievements_minimal(achievements):
                company = exp.get('company', 'this role')
                return (
                    f"For your experience at {company}, could you share more specific accomplishments? "
                    f"What measurable impact did you have? Any metrics you improved (performance, users, cost)? "
                    f"What was the scale of your impact (users affected, team size, budget)?",
                    'achievements'
                )

        return None, None