"""Technical Skills Enrichment Service - intelligently categorizes and enriches technical skills based on role."""
from __future__ import annotations

import json
import re
from typing import Dict, List, Any, Optional


class TechnicalSkillsService:
    """
    Service to analyze professional summary and user skills to intelligently populate
    primary and secondary technical skills based on detected role/technology stack.
    """
    
    # Skill mappings by role/stack
    SKILL_MAPS = {
        "java_backend": {
            "primary": [
                {"skillName": "Java (Core Java, Java 8/11/17)", "proficiency": "expert"},
                {"skillName": "Spring Framework (Spring Boot, Spring MVC, Spring Data JPA)", "proficiency": "expert"},
                {"skillName": "RESTful API Development (Microservices Architecture)", "proficiency": "expert"},
                {"skillName": "Hibernate / JPA", "proficiency": "advanced"},
                {"skillName": "SQL (MySQL, PostgreSQL, Oracle)", "proficiency": "advanced"},
                {"skillName": "Maven / Gradle", "proficiency": "advanced"},
                {"skillName": "Git (Version Control)", "proficiency": "advanced"},
            ],
            "secondary": [
                {"skillName": "Docker / Kubernetes (basic to intermediate)", "proficiency": "intermediate"},
                {"skillName": "CI/CD (Jenkins, GitHub Actions, GitLab CI)", "proficiency": "intermediate"},
                {"skillName": "Kafka / RabbitMQ (if applicable)", "proficiency": "intermediate"},
                {"skillName": "Unit Testing (JUnit, Mockito)", "proficiency": "advanced"},
                {"skillName": "Redis / Caching", "proficiency": "intermediate"},
                {"skillName": "AWS / Azure basics", "proficiency": "basic"},
                {"skillName": "SonarQube / Code Quality tools", "proficiency": "intermediate"},
            ]
        },
        "angular_frontend": {
            "primary": [
                {"skillName": "Angular (v10+ or latest)", "proficiency": "expert"},
                {"skillName": "TypeScript", "proficiency": "expert"},
                {"skillName": "JavaScript (ES6+)", "proficiency": "advanced"},
                {"skillName": "HTML5, CSS3, SCSS", "proficiency": "advanced"},
                {"skillName": "RxJS", "proficiency": "advanced"},
                {"skillName": "REST API Integration", "proficiency": "advanced"},
                {"skillName": "Angular Material / Bootstrap", "proficiency": "advanced"},
            ],
            "secondary": [
                {"skillName": "NgRx / State Management", "proficiency": "advanced"},
                {"skillName": "Jasmine / Karma (Unit Testing)", "proficiency": "advanced"},
                {"skillName": "Webpack / Build Tools", "proficiency": "intermediate"},
                {"skillName": "Performance Optimization (Lazy Loading, AOT)", "proficiency": "intermediate"},
                {"skillName": "Responsive Design", "proficiency": "advanced"},
                {"skillName": "Accessibility (a11y basics)", "proficiency": "intermediate"},
                {"skillName": "Basic Node.js", "proficiency": "basic"},
            ]
        },
        "fullstack": {
            "primary": [
                {"skillName": "Java (Spring Boot, Microservices)", "proficiency": "expert"},
                {"skillName": "Angular (v10+)", "proficiency": "expert"},
                {"skillName": "RESTful APIs (Design & Development)", "proficiency": "expert"},
                {"skillName": "SQL & Database Design", "proficiency": "advanced"},
                {"skillName": "TypeScript & JavaScript", "proficiency": "advanced"},
                {"skillName": "HTML, CSS, SCSS", "proficiency": "advanced"},
                {"skillName": "Git", "proficiency": "advanced"},
            ],
            "secondary": [
                {"skillName": "Docker & Containerization", "proficiency": "intermediate"},
                {"skillName": "CI/CD Pipelines", "proficiency": "intermediate"},
                {"skillName": "Cloud (AWS / Azure / GCP basics)", "proficiency": "basic"},
                {"skillName": "Messaging Systems (Kafka / RabbitMQ)", "proficiency": "intermediate"},
                {"skillName": "Unit & Integration Testing (JUnit, Mockito, Jasmine)", "proficiency": "advanced"},
                {"skillName": "Redis / Caching", "proficiency": "intermediate"},
                {"skillName": "Agile / Scrum", "proficiency": "intermediate"},
            ]
        }
    }
    
    # Keywords to detect role/stack
    JAVA_KEYWORDS = [
        "java", "spring", "spring boot", "spring mvc", "hibernate", "jpa",
        "maven", "gradle", "microservices", "junit", "mockito", "backend",
        "rest api", "core java"
    ]
    
    ANGULAR_KEYWORDS = [
        "angular", "typescript", "rxjs", "angular material", "ngxs", "ngrx",
        "state management", "spa", "frontend", "web development", "html5",
        "css3", "scss", "responsive design"
    ]
    
    DEVOPS_KEYWORDS = [
        "docker", "kubernetes", "ci/cd", "jenkins", "devops", "cloud",
        "aws", "azure", "gcp", "containerization", "deployment"
    ]
    
    FULLSTACK_KEYWORDS = [
        "fullstack", "full-stack", "end-to-end", "mern", "mean",
        "backend", "frontend", "database", "api"
    ]
    
    def categorize_skills(
        self,
        summary: str,
        skills: List[str],
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Intelligently categorize skills into primary and secondary based on detected role.
        
        For predefined roles (Java, Angular, Full-Stack), returns curated skill list.
        For other roles, should use async method generate_skills_with_llm() instead.
        
        Args:
            summary: Professional summary text
            skills: List of skills provided by user
            
        Returns:
            Dictionary with 'primary' and 'secondary' skill lists
        """
        # Detect role/stack
        role_type = self._detect_role(summary, skills)
        
        # Get predefined skills for the detected role
        if role_type in self.SKILL_MAPS:
            return self.SKILL_MAPS[role_type].copy()
        
        # Fallback: Return user skills categorized by position
        return self._categorize_user_skills(skills)
    
    async def categorize_skills_async(
        self,
        summary: str,
        skills: List[str],
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Intelligently categorize skills with LLM fallback for undetected roles.
        
        For predefined roles (Java, Angular, Full-Stack), returns curated skill list.
        For other roles, uses LLM to intelligently generate 7 primary + 7 secondary skills.
        
        Args:
            summary: Professional summary text
            skills: List of skills provided by user
            
        Returns:
            Dictionary with 'primary' and 'secondary' skill lists
        """
        # Detect role/stack
        role_type = self._detect_role(summary, skills)
        
        # Get predefined skills for the detected role
        if role_type in self.SKILL_MAPS:
            return self.SKILL_MAPS[role_type].copy()
        
        # For undetected roles, use LLM to generate skills intelligently
        return await self.generate_skills_with_llm(summary, skills)
    
    def _detect_and_describe_role(self, summary: str, skills: List[str]) -> str:
        """
        Detect the professional role and return a clear description.
        This role description is then used in the LLM prompt to constrain skill generation.
        """
        combined_text = (summary + " " + " ".join(skills)).lower()
        
        # Calculate scores (same as _detect_role)
        java_score = sum(combined_text.count(kw) for kw in self.JAVA_KEYWORDS)
        angular_score = sum(combined_text.count(kw) for kw in self.ANGULAR_KEYWORDS)
        
        # STRICT fullstack detection: require BOTH backend AND frontend technologies
        has_backend_tech = java_score > 3 or "spring" in combined_text or "microservice" in combined_text
        has_frontend_tech = angular_score > 3 or "typescript" in combined_text or "angular" in combined_text
        is_explicit_fullstack = "fullstack" in combined_text or "full-stack" in combined_text
        
        # Detect with strict rules
        if (has_backend_tech and has_frontend_tech) or is_explicit_fullstack:
            return "Full-Stack Developer (Backend + Frontend development)"
        elif java_score > 5 and angular_score < 2:
            return "Java Backend Developer"
        elif angular_score > 5 and java_score < 2:
            return "Angular Frontend Developer"
        elif java_score > 0 and angular_score < java_score:
            return "Java Backend Developer"
        elif angular_score > 0 and java_score < angular_score:
            return "Angular Frontend Developer"
        elif java_score > 0:
            return "Java Backend Developer"
        elif angular_score > 0:
            return "Angular Frontend Developer"
        
        # Fallback based on other keywords
        if "etl" in combined_text or "data warehouse" in combined_text:
            return "ETL Developer"
        elif "data engineer" in combined_text or "spark" in combined_text:
            return "Data Engineer"
        elif "data science" in combined_text or "ml" in combined_text:
            return "Data Scientist"
        elif "devops" in combined_text or "kubernetes" in combined_text:
            return "DevOps Engineer"
        
        return "Software Professional"
    
    def _get_role_specific_examples(self, role: str) -> str:
        """
        Return role-specific examples of skills that SHOULD be included.
        """
        examples_map = {
            "Angular Frontend Developer": 
                "✓ Angular, TypeScript, RxJS, HTML5, CSS3, Angular Material, NgRx, State Management, Responsive Design\n"
                "✓ Component Development, Template Binding, Angular Directives\n"
                "Secondary: Jasmine, Webpack, Performance Optimization, Web Accessibility",
            
            "Java Backend Developer":
                "✓ Java (Core, Spring Boot, Spring MVC, Hibernate), REST API, Microservices\n"
                "✓ SQL (MySQL, PostgreSQL, Oracle), JPA/Hibernate, Maven/Gradle\n"
                "Secondary: Docker, CI/CD, JUnit, Redis, Message Queues",
            
            "Full-Stack Developer (Backend + Frontend development)":
                "✓ Java, Spring Boot, Angular, TypeScript, REST APIs\n"
                "✓ HTML5, CSS3, Database Design, Microservices Architecture\n"
                "Secondary: Docker, Kubernetes, CI/CD, State Management",
            
            "DevOps Engineer":
                "✓ Docker, Kubernetes, CI/CD Pipelines (Jenkins), Infrastructure as Code\n"
                "✓ Cloud Platforms (AWS, Azure, GCP), Containerization, Deployment\n"
                "Secondary: Monitoring, Logging, Automation, Cloud Services",
            
            "ETL Developer":
                "✓ ETL Tools, Data Warehousing, SQL, Data Integration, Data Modeling\n"
                "✓ Performance Tuning, ETL Automation, Data Quality, Data Mapping\n"
                "Secondary: Python, Big Data, Cloud Data Warehouses, BI Tools",
            
            "Data Engineer":
                "✓ SQL, Big Data (Spark, Hadoop), Data Pipeline Development, Data Warehousing\n"
                "✓ Python/Scala, Data Modeling, ETL/ELT Processes, Cloud Platforms\n"
                "Secondary: Real-time Processing, Data Quality, Stream Processing",
        }
        
        for role_key, examples in examples_map.items():
            if role_key.lower().startswith(role.split(" ")[0].lower()):
                return examples
        
        return "Generate skills specific to the detected role"
    
    def _get_role_exclusions(self, role: str) -> str:
        """
        Return a list of skills to EXCLUDE for this role to avoid contamination.
        """
        exclusions_map = {
            "Angular Frontend Developer":
                "✗ Java, Spring Boot, Spring MVC, Hibernate, Microservices (backend-specific)\n"
                "✗ Maven, Gradle, JUnit, Docker-specific backend patterns\n"
                "✗ SQL, Database Administration (backend focus)",
            
            "Java Backend Developer":
                "✗ Angular, TypeScript, RxJS, HTML5, CSS3, Material Design (frontend-specific)\n"
                "✗ Component Development, Template Binding, Responsive Design\n"
                "✗ NgRx, State Management (frontend patterns)",
            
            "DevOps Engineer":
                "✗ Angular, TypeScript, HTML5, CSS3 (frontend technologies)\n"
                "✗ Java, Spring Boot, Hibernate (backend frameworks)\n"
                "✗ Application-specific business logic",
            
            "ETL Developer":
                "✗ Angular, React, Vue (frontend frameworks)\n"
                "✗ Java Spring Boot (backend web frameworks)\n"
                "✗ Frontend UI technologies",
            
            "Data Engineer":
                "✗ Angular, React, Vue (frontend frameworks)\n"
                "✗ Java Spring Boot, REST routing (web-specific)\n"
                "✗ UI/UX technologies",
        }
        
        for role_key, exclusions in exclusions_map.items():
            if role_key.lower().startswith(role.split(" ")[0].lower()):
                return exclusions
        
        return "Avoid skills from unrelated technology stacks"
    
    def _get_forbidden_skills_list(self, role: str) -> str:
        """
        Return an explicit list of forbidden skills for this role.
        """
        forbidden_map = {
            "Angular Frontend Developer": (
                "FORBIDDEN: Java, Spring, Spring Boot, Hibernate, Maven, Gradle, Microservices (Java), "
                "JUnit, Mockito, SQL Server, Oracle Database, Docker (backend focus), Kubernetes (backend),"
                "REST API (backend), MySQL, PostgreSQL, Backend Development, Server-Side Rendering"
            ),
            "Java Backend Developer": (
                "FORBIDDEN: Angular, Vue, React, TypeScript, RxJS, HTML5, CSS3, SCSS, Bootstrap, "
                "Material Design, Responsive Design, NgRx, Components, Templates, Frontend Development, "
                "Jasmine, Karma, Webpack (frontend)"
            ),
            "DevOps Engineer": (
                "FORBIDDEN: Angular, React, Vue, TypeScript, HTML5, CSS3, Frontend Technologies, "
                "Java, Spring Boot, Application Development, Business Logic, Database Design"
            ),
            "ETL Developer": (
                "FORBIDDEN: Angular, React, Vue, JavaScript, TypeScript, HTML5, CSS3, Frontend, "
                "Java Web Applications, Spring Boot, JSP"
            ),
            "Data Engineer": (
                "FORBIDDEN: Angular, React, HTML5, CSS3, Frontend, Java Web Frameworks, "
                "Spring Boot, JSP, Servlets"
            ),
        }
        
        for role_key, forbidden in forbidden_map.items():
            if role_key.lower().startswith(role.split(" ")[0].lower()):
                return forbidden
        
        return "Avoid skills from other technology stacks and roles"
    
    async def generate_skills_with_llm(
        self,
        summary: str,
        skills: List[str],
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Use LLM to intelligently generate technical skills for any professional role.
        CONSTRAINT: Only generate skills RELEVANT to the detected professional role.
        
        Args:
            summary: Professional summary text
            skills: List of skills provided by user
            
        Returns:
            Dictionary with 'primary' (7 skills) and 'secondary' (7 skills) skill lists
        """
        from app.services.llm_service import LLMService
        
        llm = LLMService()
        
        # Detect the role first
        detected_role = self._detect_and_describe_role(summary, skills)
        
        # Build STRICT role-specific prompt with absolute constraints
        prompt = f"""
CRITICAL INSTRUCTION: You MUST generate ONLY skills for this SPECIFIC role. NO exceptions. NO mixed skills.

DETECTED ROLE: {detected_role}

Professional Summary: {summary}
Provided Skills: {', '.join(skills)}

GENERATE EXACTLY:
- 7 PRIMARY skills (ONLY for {detected_role})
- 7 SECONDARY skills (ONLY for {detected_role})

ABSOLUTE RULES (MANDATORY):
1. ONLY use skills relevant to {detected_role}
2. DO NOT include ANY skills from other technology stacks
3. DO NOT mix different roles' technologies
4. If the detected role is "{detected_role}", generate ONLY {detected_role} skills

FORBIDDEN SKILLS TO EXCLUDE:

{self._get_forbidden_skills_list(detected_role)}

ROLE YOU MUST GENERATE FOR: {detected_role}

Approved Skills for {detected_role}:
{self._get_role_specific_examples(detected_role)}

Generate 7 PRIMARY skills (expert/advanced proficiency) + 7 SECONDARY skills (advanced/intermediate/basic).
ALL 14 SKILLS must be directly relevant to {detected_role} ONLY.

RETURN VALID JSON (no markdown):
{{
  "primary": [
    {{"skillName": "Skill 1 ONLY FOR {detected_role}", "proficiency": "expert"}},
    {{"skillName": "Skill 2 ONLY FOR {detected_role}", "proficiency": "expert"}},
    (exactly 7 primary skills - ALL SPECIFIC TO {detected_role})
  ],
  "secondary": [
    {{"skillName": "Skill 1 ONLY FOR {detected_role}", "proficiency": "advanced"}},
    (exactly 7 secondary skills - ALL SPECIFIC TO {detected_role})
  ]
}}
"""
        
        try:
            response = await llm.chat(
                [
                    {
                        "role": "system",
                        "content": "You are an expert career advisor. Generate technical skills based on professional profile. Return ONLY valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format="json_object"
            )
            
            # Parse the response
            skills_data = json.loads(response)
            
            # Validate structure
            if "primary" in skills_data and "secondary" in skills_data:
                # Ensure we have exactly 7 primary and 7 secondary
                primary = skills_data.get("primary", [])[:7]
                secondary = skills_data.get("secondary", [])[:7]
                
                # Pad if necessary
                while len(primary) < 7:
                    primary.append({"skillName": "Additional Skill", "proficiency": "advanced"})
                while len(secondary) < 7:
                    secondary.append({"skillName": "Complementary Skill", "proficiency": "intermediate"})
                
                return {
                    "primary": primary,
                    "secondary": secondary
                }
        except json.JSONDecodeError:
            pass
        except Exception as e:
            # Log error and fall back to user skills
            pass
        
        # Fallback to simple categorization if LLM fails
        return self._categorize_user_skills(skills)
    
    def _detect_role(self, summary: str, skills: List[str]) -> str:
        """
        Detect the developer role/stack based on summary and skills.
        
        Returns one of: 'java_backend', 'angular_frontend', 'fullstack', or None
        """
        combined_text = (summary + " " + " ".join(skills)).lower()
        
        # Calculate scores
        fullstack_score = sum(combined_text.count(kw) for kw in self.FULLSTACK_KEYWORDS)
        java_score = sum(combined_text.count(kw) for kw in self.JAVA_KEYWORDS)
        angular_score = sum(combined_text.count(kw) for kw in self.ANGULAR_KEYWORDS)
        
        # STRICT fullstack detection: require both backend AND frontend technologies
        # (not just "backend" or "frontend" keywords which are too generic)
        has_backend_tech = java_score > 3 or "spring" in combined_text or "microservice" in combined_text
        has_frontend_tech = angular_score > 3 or "typescript" in combined_text or "angular" in combined_text
        is_explicit_fullstack = "fullstack" in combined_text or "full-stack" in combined_text or "end-to-end" in combined_text
        
        if (has_backend_tech and has_frontend_tech) or is_explicit_fullstack:
            return "fullstack"
        elif java_score > angular_score and java_score > 0:
            return "java_backend"
        elif angular_score > java_score and angular_score > 0:
            return "angular_frontend"
        elif java_score > 0:
            return "java_backend"
        elif angular_score > 0:
            return "angular_frontend"
        
        return None
    
    def _categorize_user_skills(self, skills: List[str]) -> Dict[str, List[Dict[str, str]]]:
        """
        Fallback: Categorize user-provided skills into primary and secondary.
        Ensures minimum 7+7 structure by using provided skills as primary and 
        adding generic complementary skills as secondary.
        """
        technical_skills = {"primary": [], "secondary": []}
        
        if skills:
            # Use provided skills as primary (up to 7)
            for i, skill in enumerate(skills):
                if i < 7:
                    technical_skills["primary"].append({
                        "skillName": skill,
                        "proficiency": "advanced" if i < min(3, len(skills)) else "intermediate"
                    })
        
        # Pad primary to 7 if needed
        generic_primary_skills = [
            "Core Technical Competencies",
            "Software Development",
            "Problem Solving",
            "System Design",
            "Code Quality & Testing",
            "Performance Optimization",
            "Documentation & Best Practices"
        ]
        
        while len(technical_skills["primary"]) < 7:
            technical_skills["primary"].append({
                "skillName": generic_primary_skills[len(technical_skills["primary"])],
                "proficiency": "intermediate"
            })
        
        # Add generic secondary skills to reach 7
        generic_secondary_skills = [
            "Communication & Collaboration",
            "Continuous Learning",
            "Version Control (Git)",
            "Debugging & Troubleshooting",
            "Code Review & Mentoring",
            "Project Management Basics",
            "Agile/Scrum Methodologies"
        ]
        
        for skill in generic_secondary_skills:
            if len(technical_skills["secondary"]) < 7:
                technical_skills["secondary"].append({
                    "skillName": skill,
                    "proficiency": "intermediate"
                })
        
        return technical_skills
