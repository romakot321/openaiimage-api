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
        image = request.image
        image.name = "tmp.png"
        logger.debug(request)
        response = await self.client.images.edit(
            model="dall-e-2",
            prompt=request.prompt,
            image=image,
            size=request.size.value,
            n=1,
        )

        logger.debug(f"Get image response: {response}")
        return response.data[0].url if response.data else None

    async def generate_text2image(self, request: ExternalText2ImageTaskSchema) -> str | None:
        logger.debug(request)
        response = await self.client.images.generate(
            model="dall-e-2",
            prompt=request.prompt,
            size=request.size.value,
            n=1,
        )

        logger.debug(f"Get image response: {response}")
        return response.data[0].url if response.data else None

