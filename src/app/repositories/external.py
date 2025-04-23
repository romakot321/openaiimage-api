import os
from aiohttp import ClientSession
from pydantic import ValidationError

from app.schemas.exception import APIException
from app.schemas.external import ExternalTaskSchema


class ExternalRepository:
    EXTERNAL_API_URL = ""
    EXTERNAL_API_TOKEN = os.getenv("EXTERNAL_API_TOKEN")

    async def create_task(self, data: ExternalTaskSchema) -> str:
        async with ClientSession(
            base_url=self.EXTERNAL_API_URL,
            headers={"Authorization": "Bearer " + self.EXTERNAL_API_TOKEN},
        ) as session:
            resp = await session.post("/api/task", json=data.model_dump())
            if resp.status not in (201, 200):
                raise APIException(await resp.text())
            return (await resp.json())["id"]

    async def get_task(self, task_id: str) -> ExternalTaskSchema | None:
        async with ClientSession(
            base_url=self.EXTERNAL_API_URL,
            headers={"Authorization": "Bearer " + self.EXTERNAL_API_TOKEN},
        ) as session:
            resp = await session.get("/api/task/" + task_id)
            if resp.status != 200:
                raise APIException(await resp.text())
            body = await resp.json()
        try:
            return ExternalTaskSchema.model_validate(body)
        except ValidationError:
            return None
