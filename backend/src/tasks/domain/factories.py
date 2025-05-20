import base64
import io
from src.integration.infrastructure.external_api.openai.schemas.requests import (
    OpenAIGPT4Request,
    OpenAIGPTImage1Request,
    OpenAIGPTInput,
    OpenAIGPTInputImageContent,
    OpenAIGPTInputTextContent,
)
from src.integration.infrastructure.external_api.openai.schemas.responses import OpenAIResponse
from src.models.domain.entities import Model
from src.tasks.domain.dtos import TaskCreateImageDTO, TaskCreateTextDTO


class OpenAIGPTInputFromOpenAIResponseFactory:
    def make_image_gpt_input(self, response: OpenAIResponse) -> OpenAIGPTInput:
        return OpenAIGPTInput(
            role="assistant",
            content=[OpenAIGPTInputImageContent(image_url=response.content)]
        )

    def make_text_gpt_input(self, response: OpenAIResponse) -> OpenAIGPTInput:
        return OpenAIGPTInput(
            role="assistant",
            content=[OpenAIGPTInputTextContent(text=response.content)]
        )


class OpenAIGPTInputFromOpenAIRequestFactory:
    def make_image_gpt_input(self, request: OpenAIGPTImage1Request) -> OpenAIGPTInput:
        return OpenAIGPTInput(
            role="user",
            content=[OpenAIGPTInputImageContent(image_url=self._encode_image(image)) for image in (request.image or [])]
        )

    def make_text_gpt_input(self, request: OpenAIGPT4Request) -> OpenAIGPTInput:
        return OpenAIGPTInput(
            role="user",
            content="\n".join([inp.content[0].text for inp in request.input if hasattr(inp.content[0], "text")])
        )

    def _encode_image(self, image: io.BytesIO) -> str:
        return base64.b64encode(image.getvalue()).decode()


class OpenAIRequestFromDTOFactory:
    def make_gpt_image_1_request(
        self,
        dto: TaskCreateImageDTO,
        images: list[io.BytesIO] | None = None,
        context: list[OpenAIGPTInput] | None = None,
        model: Model | None = None
    ) -> OpenAIGPTImage1Request:
        return OpenAIGPTImage1Request(
            prompt=self._build_prompt(dto, context, model),
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
            if not gpt_input.content or isinstance(gpt_input.content, str) or not isinstance(
                gpt_input.content[0], OpenAIGPTInputImageContent
            ):
                continue
            images.append(
                io.BytesIO(
                    base64.b64decode(gpt_input.content[0].image_url.encode())
                )
            )
        return images

    def _build_prompt(
            self, dto: TaskCreateImageDTO, context: list[OpenAIGPTInput] | None = None, model: Model | None = None
    ) -> str:
        prompt = ""
        for gpt_input in context or []:
            if not gpt_input.content or isinstance(
                gpt_input.content[0], OpenAIGPTInputImageContent
            ):
                continue
            content = gpt_input.content if isinstance(gpt_input.content, str) else gpt_input.content[0].text
            prompt += f"{gpt_input.role}: {content}\n"
        if model is not None:
            model_text = model.text
            for inp in (dto.user_inputs or []):
                if inp.key in model_text:
                    model_text.format(**{inp.key: inp.value})
            prompt += model_text + "\n"
        if dto.user_prompt:
            prompt += dto.user_prompt
        return prompt
