import os
import io
import json
from loguru import logger
from uuid import uuid4
from aiohttp import ClientSession
from app.schemas.external import ExternalImageGeneration


class ExternalRepository:
    image_api_url = os.getenv("IMAGE_API_URL")
    image_api_token = os.getenv("IMAGE_API_TOKEN")

    user_id: str = str(uuid4())
    app_bundle: str = "openaiimage"

    async def start_image_generate(self, prompt: str, image_size: str) -> str:
        """Return task_id"""
        async with ClientSession(base_url=self.image_api_url, headers={"ACCESS-TOKEN": self.image_api_token}) as session:
            resp = await session.post(
                "/image",
                json={
                    "prompt": prompt,
                    "user_id": self.user_id,
                    "app_bundle": self.app_bundle,
                    "image_size": image_size
                }
            )
            assert resp.status == 201, await resp.text()
            try:
                return (await resp.json())["id"]
            except (KeyError, json.JSONDecodeError):
                return None

    async def start_image2image_generate(self, prompt: str, image_body: io.BytesIO, image_size: str) -> str:
        """Return task_id"""
        async with ClientSession(base_url=self.image_api_url, headers={"ACCESS-TOKEN": self.image_api_token}) as session:
            resp = await session.post(
                "/image/improve",
                params={
                    "prompt": prompt,
                    "user_id": self.user_id,
                    "app_bundle": self.app_bundle,
                    "image_size": image_size
                },
                data={"file": image_body}
            )
            assert resp.status == 201, await resp.text()
            try:
                return (await resp.json())["id"]
            except (KeyError, json.JSONDecodeError):
                return None

    async def get_image_generation(self, task_id: str) -> ExternalImageGeneration:
        async with ClientSession(base_url=self.image_api_url, headers={"ACCESS-TOKEN": self.image_api_token}) as session:
            resp = await session.get("/image/" + task_id)
            assert resp.status == 200, await resp.text()
            schema = ExternalImageGeneration.model_validate(await resp.json())
        logger.debug(f"Image API response: {schema.model_dump()}")
        return schema
