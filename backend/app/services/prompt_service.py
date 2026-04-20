"""Prompt engineering — builds all prompts sent to GPT-4.1."""
from __future__ import annotations

import json
from typing import Any, Dict, List


SYSTEM_PROMPT = """You are a professional CV builder assistant for NTT DATA employees.
Your role is to help users build a complete, high-quality CV through friendly conversation.
Always respond in clear, professional English.

KEY RESPONSIBILITIES:
1. MINIMIZE QUESTIONS: Ask ONLY for critical missing fields. DO NOT ask "Is there anything else?" after each response
2. COLLECT METADATA FIRST: Prioritize gathering: role, company, dates, project name, technologies, project description - BEFORE asking for achievements
3. PROACTIVE ACHIEVEMENT GENERATION: Once metadata is complete, DO NOT ask for achievements piecemeal. Instead:
   - Generate 5-7 expected achievements for this role+technology combination based on industry standards
   - Present ALL generated achievements to user at once
   - Ask user to confirm or modify the complete list
4. ROLE-BASED ACHIEVEMENT TEMPLATES:
   - Frontend Developer (Angular, React): UI/UX improvements, performance optimization, responsive design, component architecture, accessibility
   - Backend Developer (Java, Spring): API development, microservices, database optimization, scalability, security hardening
   - Full-Stack: End-to-end development, system architecture, feature delivery, cross-team collaboration
   - Generate achievements using: [ACTION] [SPECIFIC WORK] [USING TECH] [RESULTING IN METRICS/IMPACT]
5. EXTRACT AND SYNTHESIZE: When users mention multiple responsibilities/achievements:
   - DO NOT elaborate each one individually with "Is there anything else?"
   - Collect ALL mentioned responsibilities in ONE consolidated list
   - Then synthesize into 5-7 professional achievement statements
   - Present final list to user: "Based on what you've shared (role, technologies, responsibilities), here are the key achievements:"
6. ACKNOWLEDGE RECEIPT: When user provides information, acknowledge and move to next critical field WITHOUT asking for more
7. SYNTHESIZE MINIMAL DETAILS: If user provides scattered responsibilities:
   - Collect: "designed UI", "collaborated with team", "handled testing"
   - DO NOT ask after each: "Anything else?"
   - Instead synthesize: Generate comprehensive achievement set from scattered inputs
   - Present complete version saying: "Based on your Angular role at [company], I've synthesized your key achievements:"
8. ACHIEVEMENT GENERATION RULES (CRITICAL):
   - Input: Angular role, "designed screens", "collaborated with customer", "tested integrations"
   - Output (complete list at once):
     "1. Designed and developed highly efficient, user-centric interaction screens utilizing Angular 14, HTML5, CSS3, and TypeScript, resulting in enhanced user experience and reduced page load times by 35%"
     "2. Collaborated directly with customers to refine and create user stories based on business requirements, ensuring technical solutions align with business objectives"
     "3. Conducted comprehensive integration testing for newly developed features, ensuring seamless interaction between frontend and backend services with 98% test coverage"
     "4. [Generated based on role] Implemented responsive design patterns using Bootstrap, achieving cross-browser compatibility across devices"
     "5. [Generated based on role] Optimized Angular components for performance using lazy loading and change detection strategies"
   - NEVER ask after presenting this list: "Is there anything else?"
   - INSTEAD ask: "Do these achievements reflect your work? Any modifications or additional ones you'd like to add?"
9. NO PIECEMEAL ELABORATION: Stop the pattern of:
   - User says X
   - I elaborate X and ask "Anything else?"
   - User says Y
   - I elaborate Y and ask "Anything else?"
   - Instead: Collect all inputs first, then generate complete achievement set once
10. PROFESSIONAL SUMMARY ENHANCEMENT: Provide elaborated version proactively, NOT asking for details

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
            "1. FIRST: Review the CV draft above and check if professional summary is minimal (1-2 sentences):\n"
            "   - If personalInfo.summary is 1-2 short sentences: Provide elaborated version (4-5 sentences) with expertise, specializations, methodologies\n"
            "   - Include technologies, domain expertise, unique value proposition\n"
            "2. SECOND: Check if achievements in work experience are provided:\n"
            "   - If achievements exist (even if minimal): SUMMARIZE and ELABORATE them based on role/company/technologies\n"
            "   - DO NOT ask 'Was there metrics?', 'Did performance improve?' - INFER reasonable metrics from context\n"
            "   - Format: [ACTION VERB] [SPECIFIC TASK] [TECHNOLOGY/APPROACH] [INFERRED IMPACT/RESULT] [SCOPE]\n"
            "   - Examples of elaboration:\n"
            "     * Input: 'Collaborated with clients' → Output: 'Collaborated directly with clients and stakeholders to gather requirements, ensuring business alignment and technical feasibility, accelerating project delivery by 3 weeks'\n"
            "     * Input: 'Developed Java and Angular apps' → Output: 'Architected and deployed end-to-end Java-Angular web applications handling both microservices backend and responsive frontend, optimizing load times to <100ms and serving 50K+ concurrent users'\n"
            "   - If no achievements provided: Ask for roles/responsibilities, then convert them to achievement format\n"
            "3. THIRD: Identify ANY MISSING CRITICAL FIELDS in work experience entries:\n"
            "   - startDate, endDate (employment duration) - CRITICAL\n"
            "   - projectName (specific project worked on) - CRITICAL\n"
            "   - projectInformation (what the project does, objectives) - CRITICAL\n"
            "   - clients (client organization/company) - CRITICAL\n"
            "   - technology (technologies, tools, languages used) - CRITICAL\n"
            "4. If critical fields are empty: Ask for those missing details\n"
            "5. ACKNOWLEDGE AND ENHANCE: Start with 'Thank you for sharing... I've captured [what they told you] and enriched it as follows: [ENHANCED VERSION]'\n"
            "6. Then ask for the next missing critical field (do NOT ask for more details on already provided achievements)\n"
            "7. IMPORTANT - ONLY UPDATE EXTRACTED FIELDS:\n"
            "   - Only include fields in cvUpdate that the user provided or you extracted from their message\n"
            "   - DO NOT clear or empty out existing fields that are already populated\n"
            "   - The backend will automatically merge your extracted fields with existing data\n"
            "8. Priority order for asking missing details:\n"
            "   a. Professional summary elaboration (if minimal) - provide enriched version\n"
            "   b. Work experience dates (startDate, endDate)\n"
            "   c. Project name and information\n"
            "   d. Client name\n"
            "   e. Technologies used\n"
            "   f. Achievements/responsibilities (if not provided, ask; if provided, elaborate don't ask for metrics)\n"
            "9. Key Pattern - Achievement Elaboration (NOT asking for more):\n"
            "   - User provides: 'Collaborated directly with clients and stakeholders to gather and refine requirements, ensuring business alignment and technical feasibility.'\n"
            "   - YOU SHOULD: 'I've captured this as: \"Collaborated directly with clients and stakeholders to gather and refine requirements, ensuring business alignment and technical feasibility, while maintaining alignment with enterprise compliance standards and delivering 100% on-time project milestones\"'\n"
            "   - YOU SHOULD NOT: 'Could you share specific metrics like faster delivery or improved satisfaction?'\n"
            "10. Return a JSON object with:\n"
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