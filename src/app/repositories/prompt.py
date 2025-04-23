from sqlalchemy_service import BaseService as BaseRepository
from sqlalchemy import select
from uuid import UUID

from app.db.tables import Prompt


class PromptRepository[Table: Prompt, int](BaseRepository):
    base_table = Prompt

    async def create(self, model: Prompt) -> Prompt:
        self.session.add(model)
        await self._commit()
        self.response.status_code = 201
        return await self.get(model.id)

    async def list(self, is_model: bool | None = None, page=None, count=None) -> list[Prompt]:
        filters = {}
        if is_model is not None:
            filters = {"is_model": is_model}
        return list(await self._get_list(page=page, count=count, **filters))

    async def get(self, model_id: UUID) -> Prompt:
        return await self._get_one(
            id=model_id,
        )

    async def update(self, model_id: UUID, **fields) -> Prompt:
        return await self._update(model_id, **fields)

    async def delete(self, model_id: UUID):
        await self._delete(model_id)

    async def get_image(self, model_id: UUID) -> bytes | None:
        query = select(Prompt.image).filter_by(id=model_id)
        return await self.session.scalar(query)

    async def get_video_basic(self) -> Prompt:
        query = select(Prompt).filter_by(is_model=False, for_image=False, for_video=True).limit(1)
        model = await self.session.scalar(query)
        if model is None:
            raise ValueError("Not found basic prompt for video. Please create it in admin panel")
        return model

    async def get_image_basic(self) -> Prompt:
        query = select(Prompt).filter_by(is_model=False, for_image=True, for_video=False).limit(1)
        model = await self.session.scalar(query)
        if model is None:
            raise ValueError("Not found basic prompt for image. Please create it in admin panel")
        return model

