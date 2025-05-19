from src.integration.infrastructure.external_api.openai.adapter import OpenAIAdapter
from src.core.config import settings
from src.integration.infrastructure.external_api.openai.fake import FakeOpenAIAdapter


def get_openai_adapter() -> OpenAIAdapter:
    if settings.ENVIRONMENT == "prod":
        return OpenAIAdapter()
    else:
        return FakeOpenAIAdapter()

