from django.conf import settings

from apps.ai_assistant.base import AIService
from apps.ai_assistant.mock_provider import MockProvider


def get_ai_service() -> AIService:
    """Factory: AI_PROVIDER env selects OpenAI, Ollama, or mock."""
    provider = (settings.AI_PROVIDER or "openai").lower().strip()

    if provider == "mock":
        return MockProvider()

    if provider == "ollama":
        from apps.ai_assistant.ollama_provider import OllamaProvider

        return OllamaProvider()

    # openai (default) — fall back to mock when key missing so local UI still works
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("sk-your"):
        return MockProvider()

    from apps.ai_assistant.openai_provider import OpenAIProvider

    return OpenAIProvider()
