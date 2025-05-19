from openai import AsyncOpenAI

from src.integration.infrastructure.external_api.openai.schemas.requests import OpenAIGPT4Request, OpenAIGPTImage1Request
from src.integration.infrastructure.external_api.openai.schemas.responses import OpenAIResponse
from src.tasks.domain.interfaces.task_source_client import ITaskSourceClient
from src.integration.domain.exceptions import IntegrationGenerationError


class OpenAIAdapter(ITaskSourceClient[OpenAIGPTImage1Request, OpenAIGPT4Request, OpenAIResponse]):
    def __init__(self) -> None:
        super().__init__()

    async def generate_image2image(self, request: OpenAIGPTImage1Request) -> OpenAIResponse:
        client = AsyncOpenAI()
        raw_response = await client.images.with_raw_response.edit(**request.model_dump())
        response = raw_response.parse()
        if not response.data or not response.data[0].b64_json:
            raise IntegrationGenerationError(detail="Empty response")
        return OpenAIResponse(
            content=response.data[0].b64_json,
            used_tokens=response.usage.total_tokens if response.usage else None,
            remaining_requests=raw_response.headers.get("x-ratelimit-remaining-requests"),
            remaining_tokens=raw_response.headers.get("x-ratelimit-remaining-tokens"),
            reset_in=raw_response.headers.get("x-ratelimit-reset-requests"),
        )

    async def generate_text2image(self, request: OpenAIGPTImage1Request) -> OpenAIResponse:
        client = AsyncOpenAI()
        raw_response = await client.images.with_raw_response.generate(**request.model_dump(exclude="image"))
        response = raw_response.parse()
        if not response.data or not response.data[0].b64_json:
            raise IntegrationGenerationError(detail="Empty response")
        return OpenAIResponse(
            content=response.data[0].b64_json,
            used_tokens=response.usage.total_tokens if response.usage else None,
            remaining_requests=raw_response.headers.get("x-ratelimit-remaining-requests"),
            remaining_tokens=raw_response.headers.get("x-ratelimit-remaining-tokens"),
            reset_in=raw_response.headers.get("x-ratelimit-reset-requests"),
        )

    async def generate_text2text(self, request: OpenAIGPT4Request) -> OpenAIResponse:
        client = AsyncOpenAI()
        raw_response = await client.responses.with_raw_response.create(
            **request.model_dump()
        )
        response = raw_response.parse()
        return OpenAIResponse(
            content=response.output_text,
            used_tokens=response.usage.total_tokens if response.usage else None,
            remaining_requests=raw_response.headers.get("x-ratelimit-remaining-requests"),
            remaining_tokens=raw_response.headers.get("x-ratelimit-remaining-tokens"),
            reset_in=raw_response.headers.get("x-ratelimit-reset-requests"),
        )

