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
        image = request.image
        image.name = "tmp.png"
        response = await self.client.images.edit(
            model="dall-e-2",
            prompt=request.prompt,
            image=image,
            size=request.size.value,
            n=1,
        )

        logger.debug(f"Get image response: {response}")
        return response.data[0].url if response.data else None

