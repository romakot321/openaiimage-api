from sqlalchemy_service import BaseService as BaseRepository
from sqlalchemy import select
from uuid import UUID

from app.db.tables import Prompt, PromptCategory, engine


class PromptCategoryRepository[Table: PromptCategory, int](BaseRepository):
    base_table = PromptCategory
    engine = engine

    async def create(self, model: PromptCategory) -> PromptCategory:
        self.session.add(model)
        await self._commit()
        self.response.status_code = 201
        return await self.get(model.id)

    async def list(self, page=None, count=None) -> list[PromptCategory]:
        return list(await self._get_list(page=page, count=count, select_in_load=[{"parent": PromptCategory.prompts, "children": [Prompt.user_inputs]}]))

    async def get(self, model_id: UUID) -> PromptCategory:
        return await self._get_one(
            id=model_id,
            select_in_load=[{"parent": PromptCategory.prompts, "children": [Prompt.user_inputs]}]
        )

    async def update(self, model_id: UUID, **fields) -> PromptCategory:
        return await self._update(model_id, **fields)

    async def delete(self, model_id: UUID):
        await self._delete(model_id)

