from uuid import UUID
from fastapi import Depends

from app.repositories.prompt import PromptRepository
from app.schemas.models import ModelSearchSchema, ModelSchema


class ModelService:
    def __init__(
            self,
            prompt_repository: PromptRepository = Depends()
    ):
        self.prompt_repository = prompt_repository

    async def list(self, schema: ModelSearchSchema) -> list[ModelSchema]:
        prompts = await self.prompt_repository.list(is_model=True, **schema.model_dump())
        return [
            ModelSchema.model_validate(prompt)
            for prompt in prompts
        ]

    async def get_image(self, model_id: UUID) -> bytes:
        return await self.prompt_repository.get_image(model_id)

