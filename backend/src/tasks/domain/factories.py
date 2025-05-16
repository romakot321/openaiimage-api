import base64
import io
from backend.src.integration.infrastructure.external_api.openai.schemas.requests import (
    OpenAIGPT4Request,
    OpenAIGPTImage1Request,
    OpenAIGPTInput,
    OpenAIGPTInputImageContent,
    OpenAIGPTInputTextContent,
)
from backend.src.tasks.domain.dtos import TaskCreateImageDTO, TaskCreateTextDTO


class OpenAIRequestFactory:
    def make_gpt_image_1_request(
        self,
        dto: TaskCreateImageDTO,
        images: list[io.BytesIO] | None = None,
        context: list[OpenAIGPTInput] | None = None,
    ) -> OpenAIGPTImage1Request:
        return OpenAIGPTImage1Request(
            prompt=self._build_prompt(dto, context),
            size=dto.size.value,
            quality=dto.quality.value,
            image=self._build_images(images, context),
        )

    def make_gpt_4_request(
        self, dto: TaskCreateTextDTO, context: list[OpenAIGPTInput] | None = None
    ) -> OpenAIGPT4Request:
        return OpenAIGPT4Request(
            input=(context or [])
            + [
                OpenAIGPTInput(
                    role="user", content=[OpenAIGPTInputTextContent(text=dto.prompt)]
                )
            ]
        )

    def _build_images(
        self,
        images: list[io.BytesIO] | None = None,
        context: list[OpenAIGPTInput] | None = None,
    ) -> list[io.BytesIO] | None:
        if images is None:
            images = []
        if context is None:
            return images
        for gpt_input in context:
            images.append(
                io.BytesIO(
                    base64.b64decode(gpt_input.content[0].image_url.encode()).decode()
                )
            )
        return images

    def _build_prompt(
        self, dto: TaskCreateImageDTO, context: list[OpenAIGPTInput] | None = None
    ) -> str:
        prompt = ""
        for gpt_input in context or []:
            if not gpt_input.content or isinstance(
                gpt_input.content[0], OpenAIGPTInputImageContent
            ):
                continue
            prompt += f"{gpt_input.role}: {gpt_input.content[0].text}\n"
        if dto.user_prompt:
            prompt += dto.user_prompt
        return prompt
