from io import BytesIO
from typing import Literal
from pydantic import BaseModel, ConfigDict


class OpenAIGPTImage1Request(BaseModel):
    model: str = "gpt-image-1"
    prompt: str
    image: list[BytesIO] | None = None
    quality: Literal['low', 'medium', 'high', 'auto'] = 'auto'
    size: Literal["1024x1024", "1536x1024", "1024x1536"]
    n: int = 1

    model_config = ConfigDict(arbitrary_types_allowed=True)


class OpenAIGPTInputContent(BaseModel):
    type: Literal["input_image", "input_text"]


class OpenAIGPTInputImageContent(OpenAIGPTInputContent):
    type: Literal["input_image", "input_text"] = "input_image"
    image_url: str


class OpenAIGPTInputTextContent(OpenAIGPTInputContent):
    type: Literal["input_image", "input_text"] = "input_text"
    text: str


class OpenAIGPTInput(BaseModel):
    role: Literal["assistant", "system", "user", "developer"]
    content: list[OpenAIGPTInputTextContent | OpenAIGPTInputImageContent] | str


class OpenAIGPT4Request(BaseModel):
    input: list[OpenAIGPTInput]
    model: str = "gpt-4.1"
    max_output_tokens: int = 1024
