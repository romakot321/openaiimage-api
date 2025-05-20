from uuid import UUID
from fastapi_storages import FileSystemStorage
import base64

from src.contexts.domain.entities import ContextEntity, ContextEntityContentType, ContextEntityRole
from src.integration.infrastructure.external_api.openai.schemas.requests import (
    OpenAIGPTInput,
    OpenAIGPTInputImageContent,
)


class ContextEntityToOpenAIGPTInputMapper:
    def __init__(self, storage: FileSystemStorage) -> None:
        self.storage = storage

    def map(self, entities: list[ContextEntity]) -> list[OpenAIGPTInput]:
        return [
            self.map_one(entity)
            for entity in entities
        ]

    def map_one(self, entity: ContextEntity) -> OpenAIGPTInput:
        if entity.content_type == ContextEntityContentType.image:
            return self._map_image_entity(entity)
        elif entity.content_type == ContextEntityContentType.text:
            return self._map_text_entity(entity)
        raise TypeError(f"Failed to map ContextEntity: Unknown {entity.content_type=}")

    def _map_text_entity(self, entity: ContextEntity) -> OpenAIGPTInput:
        return OpenAIGPTInput(
            role=entity.role.value,
            content=entity.content
        )

    def _map_image_entity(self, entity: ContextEntity) -> OpenAIGPTInput:
        return OpenAIGPTInput(
            role=entity.role.value,
            content=[
                OpenAIGPTInputImageContent(image_url=self._encode_image(entity.content))
            ],
        )

    def _encode_image(self, filename: str) -> str:
        if len(filename) > 256:
            return filename
        if "https" in filename:
            filename = filename.rstrip("/result").rsplit("/", 1)[1]
        file = self.storage.open(filename)
        return base64.b64encode(file.read()).decode()


class OpenAIGPTInputToContextEntityMapper:
    def map_one(self, gpt_input: OpenAIGPTInput, context_id: UUID) -> ContextEntity:
        if not gpt_input.content:
            raise ValueError("Failed to map OpenAIGPTInput: Empty content")

        if isinstance(gpt_input.content, str) or hasattr(gpt_input.content[-1], "text"):
            return self._map_text_input(gpt_input, context_id)
        elif hasattr(gpt_input.content[0], "image_url"):
            return self._map_image_input(gpt_input, context_id)

        raise TypeError(f"Failed to map OpenAIGPTInput: Unknown content {gpt_input.content}")

    def _map_image_input(self, gpt_input: OpenAIGPTInput, context_id: UUID) -> ContextEntity:
        return ContextEntity(
            id=context_id,  # im too lazy for this shit
            content_type=ContextEntityContentType.image,
            content=gpt_input.content[0].image_url,
            role=ContextEntityRole(gpt_input.role),
            context_id=context_id
        )

    def _map_text_input(self, gpt_input: OpenAIGPTInput, context_id: UUID) -> ContextEntity:
        return ContextEntity(
            id=context_id,
            content_type=ContextEntityContentType.text,
            content=gpt_input.content if isinstance(gpt_input.content, str) else gpt_input.content[-1].text,
            role=ContextEntityRole(gpt_input.role),
            context_id=context_id
        )
