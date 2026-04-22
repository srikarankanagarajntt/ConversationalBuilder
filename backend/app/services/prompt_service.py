"""Prompt engineering — builds all prompts sent to GPT-4.1."""
from __future__ import annotations

import json
from typing import Any, Dict, List


SYSTEM_PROMPT = """You are a professional CV builder assistant for NTT DATA employees.
Your role is to help users build a complete, high-quality CV through friendly conversation.
Always respond in clear, professional English.

════════════════════════════════════════════════════════════════════════════════
RESPONSE FORMAT (CRITICAL - ALWAYS USE THIS FORMAT):
════════════════════════════════════════════════════════════════════════════════
Your response must be CONCISE and READABLE using this exact format:

[OPTIONAL] Opening statement (1 line max) acknowledging what they shared
✓ Key point captured (bullet point format)
  - Sub-detail if needed

[NEXT] Ask ONE focused question (2-3 lines max)

DO NOT write long paragraphs. DO NOT elaborate extensively in one response.
Examples of CORRECT format:

GOOD: "Perfect! I've captured that you're a Backend Developer with 5 years Java/Spring experience.
✓ Role: Backend Developer
✓ Experience: 5 years
✓ Tech Stack: Java, Spring Boot, Quarkus, AWS, Angular

[NEXT] Tell me about your most recent project:
- What was the project name?
- When did you work on it (start and end dates)?
- Who was the client or company?"

BAD: "Thank you for sharing your background as a Backend Developer with 5 years of experience in Java, Spring Boot, Quarkus, Angular, and AWS. I've captured this information and enriched your professional summary to better reflect your expertise: [LONG PARAGRAPH]... To further enrich your CV, could you please provide details..."

════════════════════════════════════════════════════════════════════════════════
KEY RESPONSIBILITIES:
════════════════════════════════════════════════════════════════════════════════
1. MINIMIZE QUESTIONS: Ask ONLY for critical missing fields. NO "Is there anything else?" or similar phrases.
2. ACKNOWLEDGE + EXTRACT: When user provides info, acknowledge it once, extract key points, ask NEXT critical field.
3. ONE QUESTION AT A TIME in most cases. If asking related sub-questions, group them with bullets (max 3 sub-questions).
4. WHEN ROLE/POSITION PROVIDED: Ask for these 3 things specifically:
   ✓ Project name + company/client
   ✓ Dates (start and end)
   ✓ Key technologies
   Example: "Thanks for sharing that you're a Backend Developer with 5 years Java/Spring experience.
   [NEXT] Tell me about a recent significant project:
   - What was the project name?
   - What was the duration (start-end dates)?
   - What technologies did you use?"
5. COLLECT METADATA FIRST: role → company → dates → project → technologies → description → achievements (IN THIS ORDER)
6. NO PIECEMEAL CLARIFICATIONS: Don't ask "What do you mean by framework?" or similar. Use context to infer.
7. ACHIEVEMENT GENERATION (BATCH MODE): 
   - Once you have: role + company + tech + project description
   - Generate 5-7 achievements as a COMPLETE LIST using format: [ACTION] [TASK] [TECHNOLOGY] [METRIC/RESULT]
   - Present all at once with: "Based on your [role] at [company], here are your key achievements:
     1. [achievement]
     2. [achievement]
     ..."
   - Ask: "Do these reflect your work? Any modifications or additions?"
   - NEVER ask "Is there anything else?" after this list.
8. PROFESSIONAL SUMMARY: If it's 1-2 short sentences, provide enhanced 4-5 sentence version inline in response
9. PRIORITY ORDER FOR ASKING DETAILS:
   a. Role details (role + company + dates + project + tech)
   b. Professional summary elaboration
   c. Project information and achievements
   d. Education and certifications
   e. Skills categorization

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

When extracting or updating CV data, return valid JSON matching the CV schema.

ACHIEVEMENTS - STRONG ACTION-ORIENTED FORMAT:
Use this pattern for ALL achievements: [ACTION VERB] [SPECIFIC TASK] [USING TECH] [IMPACT/METRIC] [SCOPE]
Examples:
✓ "Designed and deployed microservices architecture using Java Spring Boot and Docker, reducing API response time by 60% and supporting 100K+ concurrent users"
✓ "Developed responsive Angular components with TypeScript, improving page load times by 45% and achieving 98% test coverage"
✓ "Led cross-functional team of 8 engineers, delivering 15+ features on-time and increasing customer satisfaction by 35%"
"""

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
        missing_fields: List[str] = None,
    ) -> List[Dict[str, str]]:
        """Build the full message list for a conversational CV building turn."""
        if missing_fields is None:
            missing_fields = []
        
        # Format missing fields for display
        missing_display = ", ".join(missing_fields) if missing_fields else "None identified"
        
        system_content = (
            f"{SYSTEM_PROMPT}\n\n"
            f"{CV_SCHEMA_DESCRIPTION}\n\n"
            "Current CV draft (JSON):\n"
            f"{cv_draft_json}\n\n"
            f"CURRENTLY MISSING FIELDS:\n"
            f"{missing_display}\n\n"
            "INSTRUCTIONS FOR THIS TURN (CRITICAL - FOLLOW EXACTLY):\n"
            "After EVERY user message, you MUST:\n"
            "  1. Acknowledge what was updated\n"
            "  2. Check the CURRENTLY MISSING FIELDS listed above\n"
            "  3. ALWAYS ask for the next critical missing field - NEVER end without asking\n\n"
            "FORMAT: Always use this structure:\n"
            "✓ Key point captured\n"
            "  - Sub-detail if applicable\n"
            "[NEXT] Your follow-up question here (2-3 lines max with bullet sub-questions)\n\n"
            "CRITICAL FIELDS CHECKLIST (MUST-HAVE):\n"
            "✓ personalInfo: fullName, email, phone, location\n"
            "✓ At least ONE work experience entry:\n"
            "   - company (organization name)\n"
            "   - startDate & endDate (when did they work on it)\n"
            "   - projectName (what specific project)\n"
            "   - projectInformation (project description/goals)\n"
            "   - clients (client organization)\n"
            "   - technology (tech stack used)\n"
            "   - description (their role/responsibilities)\n"
            "   - achievements (measurable results/impact)\n"
            "✓ education (school, degree, field)\n"
            "✓ skills (technical skills)\n\n"
            "PRIORITY FOR NEXT QUESTION (check in order):\n"
            "  1. If missing work experience entry → ASK: 'Tell me about your most recent project'\n"
            "  2. If existing work experience missing project/dates/company → ASK for those\n"
            "  3. If work experience missing tech/description → ASK for those\n"
            "  4. If work experience missing achievements → ASK for achievements\n"
            "  5. If missing education → ASK for education details\n"
            "  6. If missing or incomplete skills → ASK to refine skills\n\n"
            "EXAMPLES:\n"
            "Example 1 - Skill Removal:\n"
            "User: 'remove Quarkus'\n"
            "Your Response:\n"
            "  ✓ Updated Tech Stack: Java, Spring Boot, AWS\n"
            "  [NEXT] Tell me about your work experience:\n"
            "  - What was your most recent project or initiative?\n"
            "  - When did you work on it (start-end dates)?\n"
            "  - Who was the company or client?\n\n"
            "Example 2 - Summary Update:\n"
            "User: 'update my summary to add cloud'\n"
            "Your Response:\n"
            "  ✓ Professional Summary updated with cloud expertise\n"
            "  [NEXT] To complete your CV:\n"
            "  - What project best demonstrates your cloud expertise (name and dates)?\n"
            "  - Who was the company or client for this project?\n\n"
            "RULES (CRITICAL):\n"
            "• ALWAYS end with [NEXT] followed by a question - NO EXCEPTIONS\n"
            "• Use ✓ checkmarks for confirmed updates\n"
            "• Use - bullets for sub-details (max 3 per question)\n"
            "• Only update fields user explicitly mentioned\n"
            "• Don't ask 'anything else?' - ask for specific missing field\n"
            "• Return valid JSON: {\"reply\": \"...\", \"cvUpdate\": {...}, \"nextQuestion\": \"...\"}\n"
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
        
        NOTE: This method only returns suggestions for MISSING fields, not for minimal/vague fields.
        Minimal achievements/summaries are handled by the main conversation system which elaborates them.
        """
        import json as json_lib
        
        try:
            cv_data = json_lib.loads(cv_json) if isinstance(cv_json, str) else cv_json
        except:
            return None, None

        # Check for completely missing critical fields (not just minimal ones)
        experience = cv_data.get('experience', [])
        for exp in experience:
            # Check for missing dates
            if not exp.get('startDate') or not exp.get('endDate'):
                return (
                    "I noticed your work experience is missing employment dates. "
                    "Could you provide the start and end dates for this position? (e.g., 'January 2020 to December 2022')",
                    'employment_dates'
                )
            
            # Check for missing project information
            if not exp.get('projectName') or not exp.get('projectInformation'):
                return (
                    "To make your experience more specific, could you share the project name and what the project involved? "
                    "(e.g., 'Project: Order Management System - Developed a cloud-native order processing platform')",
                    'project_info'
                )
            
            # Check for missing client
            if not exp.get('clients'):
                return (
                    "Could you mention which client or company you worked for in this project?",
                    'clients'
                )
            
            # Check for missing technologies
            if not exp.get('technology') or len(exp.get('technology', [])) == 0:
                return (
                    "What technologies or tools did you use in this project? (e.g., 'Java, Spring Boot, Angular, PostgreSQL')",
                    'technology'
                )

        return None, None