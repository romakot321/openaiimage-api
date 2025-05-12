from app.schemas.external import ExternalImageSize, ExternalImage2ImageTaskSchema, ExternalText2ImageTaskSchema
from openai import AsyncOpenAI
from loguru import logger
import io
import base64
import json


class OpenAIRepository:
    def __init__(self):
        self.client = AsyncOpenAI()

    async def generate_image2image(self, request: ExternalImage2ImageTaskSchema) -> str | None:
        images = request.images
        for image in images:
            image.name = "tmp.png"
        response = await self.client.images.edit(
            model="gpt-image-1",
            prompt=request.prompt,
            image=images,
            size=request.size.value,
            n=1,
        )

        logger.debug(f"Get image response for: {request=} {response.usage}")
        return response.data[0].b64_json if response.data else None

    async def generate_text2image(self, request: ExternalText2ImageTaskSchema) -> str | None:
        response = await self.client.images.generate(
            model="gpt-image-1",
            prompt=request.prompt,
            size=request.size.value,
            n=1,
        )

        logger.debug(f"Get image response for: {request=} {response.usage}")
        return response.data[0].b64_json if response.data else None

