from app.schemas.external import (
    ExternalImageSize,
    ExternalImage2ImageTaskSchema,
    ExternalResponse,
    ExternalText2ImageTaskSchema,
    ExternalText2TextTaskSchema,
)
from openai import AsyncOpenAI
from loguru import logger
import io
import base64
import json


class OpenAIRepository:
    def __init__(self):
        self.client = AsyncOpenAI()

    async def generate_text2text(
        self, request: ExternalText2TextTaskSchema
    ) -> ExternalResponse:
        raw_response = await self.client.responses.with_raw_response.create(
            **request.model_dump()
        )
        response = raw_response.parse()
        return ExternalResponse(
            content=response.output_text,
            remaining_requests=raw_response.headers.get("x-ratelimit-remaining-requests"),
            remaining_tokens=raw_response.headers.get("x-ratelimit-remaining-tokens"),
            reset_in=raw_response.headers.get("x-ratelimit-reset-requests"),
        )

    async def generate_image2image(
        self, request: ExternalImage2ImageTaskSchema
    ) -> ExternalResponse:
        images = request.images
        for image in images:
            image.name = "tmp.png"
        raw_response = await self.client.images.with_raw_response.edit(
            model="gpt-image-1",
            prompt=request.prompt,
            image=images,
            quality=request.quality.value,
            size=request.size.value,
            n=1,
        )
        response = raw_response.parse()

        logger.debug(f"Get image response for: {request=} {response.usage}")
        return ExternalResponse(
            content=response.data[0].b64_json if response.data else None,
            remaining_requests=raw_response.headers.get("x-ratelimit-remaining-requests"),
            remaining_tokens=raw_response.headers.get("x-ratelimit-remaining-tokens"),
            reset_in=raw_response.headers.get("x-ratelimit-reset-requests"),
        )

    async def generate_text2image(
        self, request: ExternalText2ImageTaskSchema
    ) -> ExternalResponse:
        raw_response = await self.client.images.with_raw_response.generate(
            model="gpt-image-1",
            prompt=request.prompt,
            size=request.size.value,
            n=1,
        )
        response = raw_response.parse()

        logger.debug(f"Get image response for: {request=} {response.usage}")
        return ExternalResponse(
            content=response.data[0].b64_json if response.data else None,
            remaining_requests=raw_response.headers.get("x-ratelimit-remaining-requests"),
            remaining_tokens=raw_response.headers.get("x-ratelimit-remaining-tokens"),
            reset_in=raw_response.headers.get("x-ratelimit-reset-requests"),
        )
