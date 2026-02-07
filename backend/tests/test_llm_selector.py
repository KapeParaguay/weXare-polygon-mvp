from app.llm.selector import LLMSelector
from app.core.config import settings


def test_llm_selector_prefers_openai(monkeypatch):
    monkeypatch.setattr(settings, "openai_api_key", "x")
    monkeypatch.setattr(settings, "openrouter_api_key", "")
    monkeypatch.setattr(settings, "llm_provider_priority", "openai,openrouter")
    llm = LLMSelector().get()
    assert llm is not None
    assert llm.name == "openai"


def test_llm_selector_fallback_openrouter(monkeypatch):
    monkeypatch.setattr(settings, "openai_api_key", "")
    monkeypatch.setattr(settings, "openrouter_api_key", "y")
    monkeypatch.setattr(settings, "llm_provider_priority", "openai,openrouter")
    llm = LLMSelector().get()
    assert llm is not None
    assert llm.name == "openrouter"
