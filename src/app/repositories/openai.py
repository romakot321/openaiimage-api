from app.schemas.external import ExternalImageSize, ExternalTaskSchema
from openai import AsyncOpenAI
from loguru import logger
import io
import base64
import json


class OpenAIRepository:
    def __init__(self):
        self.client = AsyncOpenAI()

    async def generate_image2image(self, request: ExternalTaskSchema) -> str | None:
        response = await self.client.images.generate(
            model="dall-e-2",
            prompt=request.prompt,
            image=request.image,
            size=request.size.value,
            quality="standard",
            n=1,
        )

        logger.debug(f"Get image response: {response}")
        return response.data[0].url if response.data else None

