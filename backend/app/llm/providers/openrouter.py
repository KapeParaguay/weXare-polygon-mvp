import httpx
from app.core.config import settings
from app.llm.providers.base import LLMProvider, LLMResponse


class OpenRouterProvider(LLMProvider):
    name = "openrouter"

    def available(self) -> bool:
        return bool(settings.openrouter_api_key)

    def generate(self, prompt: str) -> LLMResponse:
        headers = {"Authorization": f"Bearer {settings.openrouter_api_key}"}
        payload = {
            "model": settings.llm_model_openrouter,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        r = httpx.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        text = data["choices"][0]["message"]["content"]
        return LLMResponse(text=text)
