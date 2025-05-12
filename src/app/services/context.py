from enum import Enum
from uuid import UUID
from fastapi import Depends, HTTPException, status
from app.db.tables import Context, ContextEntityContentType, ContextEntityRole
from app.repositories.context import ContextRepository
from app.repositories.context_entity import ContextEntityRepository
from app.schemas.context import ContextBuilded, ContextBuildedEntity, ContextCreateSchema, ContextEntitySchema, ContextSchema


class ContextService:
    MAX_TEXT_LENGTH = 30000
    MAX_IMAGES_COUNT = 15

    def __init__(
        self,
        context_repository: ContextRepository = Depends(ContextRepository.depend),
        entity_repository: ContextEntityRepository = Depends(
            ContextEntityRepository.depend
        ),
    ) -> None:
        self.context_repository = context_repository
        self.entity_repository = entity_repository

    async def create(self, schema: ContextCreateSchema) -> ContextSchema:
        model = await self.context_repository.create(**schema.model_dump())
        return ContextSchema.model_validate(model.__dict__ | {"text_available": self.MAX_TEXT_LENGTH, "images_available": self.MAX_IMAGES_COUNT})

    async def get(self, context_id: UUID) -> ContextSchema:
        model = await self.context_repository.get(context_id)
        usage = await self._get_usage(context_id)
        return ContextSchema.model_validate(model.__dict__ | {"text_available": self.MAX_TEXT_LENGTH - usage["text"], "images_available": self.MAX_IMAGES_COUNT - usage["image"]})

    async def delete(self, context_id: UUID):
        await self.context_repository.delete(context_id)

    async def _get_usage(self, context_id: UUID) -> dict[str, int]:
        builded = await self.build_context(context_id)
        text_length = len("".join(map(lambda i: i.content if i.content not in builded.images_filenames else '', builded.entities)))
        images_count = len(builded.images_filenames)
        return {"text": text_length, "images": images_count}

    async def add_entity_text(
        self, context_id: UUID, content: str, role: ContextEntityRole
    ) -> ContextEntitySchema:
        usage = await self._get_usage(context_id)
        if usage["text"] + len(content) >= self.MAX_TEXT_LENGTH:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Max context size exceed")
        model = await self.entity_repository.create(
            context_id=context_id,
            content=content,
            content_type=ContextEntityContentType.text,
            role=role,
        )
        return ContextEntitySchema.model_validate(model)

    async def add_entity_image(
        self, context_id: UUID, image_filename: str, role: ContextEntityRole
    ) -> ContextEntitySchema:
        usage = await self._get_usage(context_id)
        if usage["images"] + 1 > self.MAX_IMAGES_COUNT:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Max context size exceed")
        model = await self.entity_repository.create(
            context_id=context_id,
            content=image_filename,
            content_type=ContextEntityContentType.image,
            role=role,
        )
        return ContextEntitySchema.model_validate(model)

    async def build_context(self, context_id: UUID) -> ContextBuilded:
        model = await self.context_repository.get(context_id)
        schema = ContextBuilded(entities=[], images_filenames=[])
        for entity in model.entities:
            if entity.content_type == ContextEntityContentType.text:
                schema.entities.append(ContextBuildedEntity(role=entity.role, content=entity.content))
            elif entity.content_type == ContextEntityContentType.image:
                schema.entities.append(ContextBuildedEntity(role=entity.role, content=entity.content))
                schema.images_filenames.append(entity.content)
        return schema

    async def __aenter__(self):
        self.context_repository = await ContextRepository().__aenter__()
        self.entity_repository = ContextEntityRepository(session=self.context_repository.session)
        return self

    async def __aexit__(self, *excinfo):
        await self.context_repository.__aexit__(*excinfo)
