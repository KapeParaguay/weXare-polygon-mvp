from app.core.config import settings
from app.llm.providers.openai import OpenAIProvider
from app.llm.providers.openrouter import OpenRouterProvider
from app.llm.providers.base import LLMProvider


class LLMSelector:
    def __init__(self):
        self.providers: dict[str, LLMProvider] = {
            "openai": OpenAIProvider(),
            "openrouter": OpenRouterProvider(),
        }

    def get(self) -> LLMProvider | None:
        order = [p.strip() for p in settings.llm_provider_priority.split(",") if p.strip()]
        for name in order:
            provider = self.providers.get(name)
            if provider and provider.available():
                return provider
        return None
