import asyncio
import openai
from src.integration.infrastructure.external_api.openai.schemas.requests import OpenAIGPT4Request, OpenAIGPTImage1Request
from src.integration.infrastructure.external_api.openai.schemas.responses import OpenAIResponse
from src.tasks.domain.interfaces.task_source_client import ITaskSourceClient


class FakeTaskSourceClient(ITaskSourceClient):
    _remaining_requests = 2
    _remaining_tokens = 2
    _reset_in = "1m0s"
    webhook_domain = None

    def _substract_remaining(self):
        if self._remaining_requests <= 0 or self._remaining_tokens <= 0:
            raise openai._exceptions.OpenAIError()
        self._remaining_tokens -= 1
        self._remaining_requests -= 1

    async def generate_image2image(self, request: OpenAIGPTImage1Request) -> OpenAIResponse:
        self._substract_remaining()
        await asyncio.sleep(0.5)
        return OpenAIResponse(
            content=request.prompt,
            used_tokens=len(request.prompt),
            remaining_requests=self._remaining_requests,
            remaining_tokens=self._remaining_tokens,
            reset_in=self._reset_in
        )

    async def generate_text2image(self, request: OpenAIGPTImage1Request) -> OpenAIResponse:
        self._substract_remaining()
        await asyncio.sleep(0.5)
        return OpenAIResponse(
            content=request.prompt,
            used_tokens=len(request.prompt),
            remaining_requests=self._remaining_requests,
            remaining_tokens=self._remaining_tokens,
            reset_in=self._reset_in
        )

    async def generate_text2text(self, request: OpenAIGPT4Request) -> OpenAIResponse:
        self._substract_remaining()
        await asyncio.sleep(0.5)
        prompt = "".join(i.content[0].text for i in request.input)
        return OpenAIResponse(
            content=prompt,
            used_tokens=len(prompt),
            remaining_requests=self._remaining_requests,
            remaining_tokens=self._remaining_tokens,
            reset_in=self._reset_in
        )
