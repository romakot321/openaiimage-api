from backend.src.integration.infrastructure.external_api.openai.adapter import OpenAIAdapter


def get_openai_adapter() -> OpenAIAdapter:
    return OpenAIAdapter()
