from io import BytesIO
from typing import Literal
import base64
from pydantic import BaseModel, ConfigDict, field_serializer, field_validator, SerializationInfo


class OpenAIGPTImage1Request(BaseModel):
    model: str = "gpt-image-1"
    prompt: str
    image: list[BytesIO] | None = None
    quality: Literal['low', 'medium', 'high', 'auto'] = 'auto'
    size: Literal["1024x1024", "1536x1024", "1024x1536"]
    n: int = 1

    @field_serializer("image", when_used='json')
    def encode_image(self, value: list[BytesIO] | None, _info):
        if value is None:
            return value
        return [base64.b64encode(im.getvalue()).decode() for im in value]

    @field_validator("image", mode="before")
    @classmethod
    def decode_image(cls, value: list[BytesIO] | list[str] | None) -> list[BytesIO] | None:
        if value is None:
            return value
        if not isinstance(value, list) or not value:
            return value
        if isinstance(value[0], BytesIO):
            return value
        ret = []
        for im in value:
            buf = BytesIO(base64.b64decode(im.encode()))
            buf.name = "tmp.png"
            ret.append(buf)
        return ret

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
