from uuid import UUID
from fastapi import Depends
from app.repositories.prompt_category import PromptCategoryRepository
from app.schemas.model_category import ModelCategorySchema, ModelCategorySearchSchema


class ModelCategoryService:
    def __init__(self, category_repository: PromptCategoryRepository = Depends(PromptCategoryRepository.depend)) -> None:
        self.category_repository = category_repository

    async def get_list(self, schema: ModelCategorySearchSchema) -> list[ModelCategorySchema]:
        models = await self.category_repository.list(**schema.model_dump(exclude_none=True))
        return [
            ModelCategorySchema.model_validate(model)
            for model in models
        ]

    async def get(self, category_id: UUID) -> ModelCategorySchema:
        model = await self.category_repository.get(category_id)
        return ModelCategorySchema.model_validate(model)
