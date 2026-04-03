class OpenAIAdapter:
    async def generate_structured_response(self, prompt: str) -> dict:
        return {
            "assistant_message": "Thanks. Please share your current responsibilities and primary technical skills.",
            "updates": {
                "header": {"fullName": "Mock Candidate", "jobTitle": "System Integration Specialist"},
                "professionalSummary": ["Experienced software professional with strong frontend and API integration skills."]
            },
        }

_openai_adapter = OpenAIAdapter()

def get_openai_adapter() -> OpenAIAdapter:
    return _openai_adapter
