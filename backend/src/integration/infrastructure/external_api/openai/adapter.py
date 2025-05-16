import io
from openai import AsyncOpenAI

from backend.src.integration.infrastructure.external_api.openai.schemas.requests import OpenAIGPT4Request, OpenAIGPTImage1Request
from backend.src.integration.infrastructure.external_api.openai.schemas.responses import OpenAIResponse
from backend.src.tasks.domain.interfaces.task_source_client import ITaskSourceClient
from backend.src.integration.domain.exceptions import IntegrationGenerationError


class OpenAIAdapter(ITaskSourceClient[OpenAIGPTImage1Request, OpenAIGPT4Request, OpenAIResponse]):
    def __init__(self) -> None:
        super().__init__()

        self.client = AsyncOpenAI()

    async def generate_image2image(self, request: OpenAIGPTImage1Request) -> OpenAIResponse:
        raw_response = await self.client.images.with_raw_response.edit(**request.model_dump())
        response = raw_response.parse()
        if not response.data or not response.data[0].b64_json:
            raise IntegrationGenerationError(detail="Empty response")
        return OpenAIResponse(
            content=response.data[0].b64_json,
            remaining_requests=raw_response.headers.get("x-ratelimit-remaining-requests"),
            remaining_tokens=raw_response.headers.get("x-ratelimit-remaining-tokens"),
            reset_in=raw_response.headers.get("x-ratelimit-reset-requests"),
        )

    async def generate_text2image(self, request: OpenAIGPTImage1Request) -> OpenAIResponse:
        raw_response = await self.client.images.with_raw_response.generate(**request.model_dump())
        response = raw_response.parse()
        if not response.data or not response.data[0].b64_json:
            raise IntegrationGenerationError(detail="Empty response")
        return OpenAIResponse(
            content=response.data[0].b64_json,
            remaining_requests=raw_response.headers.get("x-ratelimit-remaining-requests"),
            remaining_tokens=raw_response.headers.get("x-ratelimit-remaining-tokens"),
            reset_in=raw_response.headers.get("x-ratelimit-reset-requests"),
        )

    async def generate_text2text(self, request: OpenAIGPT4Request) -> OpenAIResponse:
        raw_response = await self.client.responses.with_raw_response.create(
            **request.model_dump()
        )
        response = raw_response.parse()
        return OpenAIResponse(
            content=response.output_text,
            remaining_requests=raw_response.headers.get("x-ratelimit-remaining-requests"),
            remaining_tokens=raw_response.headers.get("x-ratelimit-remaining-tokens"),
            reset_in=raw_response.headers.get("x-ratelimit-reset-requests"),
        )

