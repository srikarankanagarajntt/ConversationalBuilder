from app.adapters.openai_adapter import OpenAIAdapter, get_openai_adapter

class LLMService:
    def __init__(self, adapter: OpenAIAdapter) -> None:
        self.adapter = adapter

    async def continue_conversation(self, prompt: str) -> dict:
        return await self.adapter.generate_structured_response(prompt)

_llm_service = LLMService(adapter=get_openai_adapter())

def get_llm_service() -> LLMService:
    return _llm_service
